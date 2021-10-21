import os
import warnings
from collections import OrderedDict
from itertools import chain
from typing import List, Iterator, Tuple, Optional, Any, Union

import click
from hbutils.reflection import quick_import_object

from .base import CONTEXT_SETTINGS
from .io import _import_trees_from_package
from .utils import err_validator, multiple_validator, validator, _click_pending
from ...tree import TreeValue
from ...tree import dump as dump_treevalue


@err_validator((ImportError,))
@multiple_validator
@validator
def validate_trees(value: str):
    _items = [item.strip() for item in value.split(':', maxsplit=2)]
    return _import_trees_from_package(*_items, default_template='$name.btv')


_DEFAULT_COMPRESS_VALUE = 'zlib'


@err_validator((ImportError,))
@validator
def validate_compress(value: Optional[str] = None):
    _tuple = tuple([quick_import_object(item)[0]
                    for item in (value or _DEFAULT_COMPRESS_VALUE).split(':', maxsplit=2)])
    if len(_tuple) == 2:
        return _tuple, value
    else:
        return _tuple[0], value


def _export_cli(cli: click.Group):
    @cli.command('export', help='Export trees to binary files, compression is available.',
                 context_settings=CONTEXT_SETTINGS)
    @click.option('-t', '--tree', 'trees', type=click.UNPROCESSED, callback=validate_trees,
                  multiple=True, help='Trees to be imported from packages, such as \'-t my_tree.t1\'.')
    @click.option('-o', '--output', 'outputs', type=click.types.Path(dir_okay=False),
                  multiple=True, help='Output file path, multiple output is supported.')
    @click.option('-d', '--directory', 'directory',
                  type=click.types.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
                  default=None, help='Directory to save the exported trees.')
    @click.option('-c', '--compress', 'compress', type=click.UNPROCESSED, callback=validate_compress,
                  default=None, help='Compress algorithm, can be a single lib name or a tuple, default use \'zlib\'.')
    @click.option('-r', '--raw', 'no_compress', is_flag=True, default=False,
                  help='Disable all the compression, just export the raw data.', show_default=True)
    def _export(trees: List[Iterator[Tuple[TreeValue, str]]],
                outputs: List[str], directory: Optional[str],
                compress: Tuple[Union[Tuple[Any, Any], Any], Optional[str]], no_compress: bool):
        trees = [(v, k) for k, v in OrderedDict([(k, v) for v, k in chain(*trees)]).items()]
        directory = os.path.abspath(directory or '.')

        compress, _compress_value = compress
        if _compress_value and no_compress:
            warnings.warn(RuntimeWarning('Compression is disabled due to -r option, '
                                         'compression assigned in -c option will be ignored.'))
        compress = None if no_compress else compress

        if 0 < len(outputs) < len(trees):
            warnings.warn(RuntimeWarning(f'{len(trees)} tree(s) detected but only {len(outputs)} outputs found, '
                                         f'the tress without output will use their default names.'))
        if len(outputs) > len(trees):
            warnings.warn(RuntimeWarning(f'{len(trees)} tree(s) detected but {len(outputs)} outputs found, '
                                         f'the excess outputs will be ignored.'))

        outputs = list(outputs[:len(trees)])
        outputs += [None] * (len(trees) - len(outputs))
        for (tree, name), fname in zip(trees, outputs):
            _actual_path = os.path.join(directory, fname or name)
            with _click_pending(f'Exporting tree {repr(name)} to binary file {repr(_actual_path)} ... '):
                with open(_actual_path, 'wb') as file:
                    dump_treevalue(tree, file=file, compress=compress)

    return cli
