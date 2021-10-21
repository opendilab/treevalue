import codecs
import os
import shutil
import tempfile
import warnings
from collections import OrderedDict
from functools import partial
from itertools import chain
from typing import Tuple, List, Optional, Iterator, Union

import click
from graphviz import Digraph, Graph
from hbutils.reflection import quick_import_object

from .base import CONTEXT_SETTINGS
from .io import _import_trees_from_binary, _import_trees_from_package
from .utils import multiple_validator, _click_pending, err_validator, validator
from ...tree import TreeValue, graphics


@err_validator((ImportError,))
@multiple_validator
@validator
def validate_trees(value: str) -> Iterator[Tuple[TreeValue, str]]:
    _items = [item.strip() for item in value.split(':', maxsplit=2)]
    return chain(_import_trees_from_binary(*_items), _import_trees_from_package(*_items))


@err_validator((ImportError,))
@validator
def validate_graph(value: str):
    if value is None:
        return value

    _graph, _, _ = quick_import_object(value, lambda g: isinstance(g, (Graph, Digraph)))
    return _graph


@multiple_validator
@validator
def validate_cfg(value: str) -> Tuple[str, str]:
    _items = value.split('=', maxsplit=2)
    if len(_items) < 2:
        raise click.BadParameter(f'Configuration should be KEY=VALUE, but {repr(value)} found.')

    key, value = _items
    return key, value


@err_validator((ImportError,))
@multiple_validator
@validator
def validate_duplicate_types(value: str):
    _it, _, _ = quick_import_object(value, lambda t: isinstance(t, type))
    return _it


def _save_source_code(g: Digraph, path: str):
    with codecs.open(path, 'w') as file:
        file.write(g.source)


def _save_image(g: Digraph, path: str, fmt: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        with tempfile.NamedTemporaryFile(dir=tmpdir) as tmpfile:
            svg_file = g.render(tmpfile.name, format=fmt)
            shutil.copy(svg_file, path)


_IMAGE_FMTS = {'svg', 'png'}


def _save_graph_fmt_infer(path: str, fmt: Optional[str] = None):
    if not fmt:
        _basename, _extname = os.path.splitext(path)
        if _extname:
            fmt = _extname[1:]
    return fmt if fmt else None


def _save_graph(g: Digraph, path: str, fmt: str):
    path = os.path.abspath(path)
    _saver = partial(_save_image, fmt=fmt) if fmt in _IMAGE_FMTS else _save_source_code
    return _saver(g, path)


def _graph_cli(cli: click.Group):
    @cli.command('graph', help='Generate graph by trees and graphviz elements.',
                 context_settings=CONTEXT_SETTINGS)
    @click.option('-t', '--tree', 'trees', type=click.UNPROCESSED, callback=validate_trees,
                  multiple=True, help='Trees to be imported, such as \'-t my_tree.t1\'.')
    @click.option('-g', '--graph', type=click.UNPROCESSED, callback=validate_graph,
                  help='Graph to be exported, such as \'-g my_script.graph1\', '
                       '-t options will be ignored.')
    @click.option('-c', '--config', 'configs', type=click.UNPROCESSED, callback=validate_cfg,
                  multiple=True, help='External configuration when generating graph. '
                                      'Like \'-c bgcolor=#ffffff00\', will be displayed as '
                                      'graph [bgcolor=#ffffff00] in source code. ')
    @click.option('-T', '--title', type=str, default=None,
                  help='Title of the graph, will be automatically generated when not given.')
    @click.option('-o', '--output', 'outputs', type=click.types.Path(dir_okay=False),
                  multiple=True, help='Output file path, multiple output is supported.')
    @click.option('-O', '--stdout', 'print_to_stdout', is_flag=True, default=False,
                  help='Print graphviz source code to stdout, -o option will be ignored.', show_default=True)
    @click.option('-F', '--format', 'fmt', type=str, required=False,
                  help='Format of output file.')
    @click.option('-d', '--duplicate', 'dups', type=click.UNPROCESSED, callback=validate_duplicate_types,
                  multiple=True, help='The types need to be duplicated, '
                                      'such as \'-d numpy.ndarray\', \'-d torch.Tensor\' and \'-d set\'.')
    @click.option('-D', '--duplicate_all', 'duplicate_all', is_flag=True, default=False,
                  help='Duplicate all the nodes of values with same memory id.', show_default=True)
    def _graph(trees: List[Iterator[Tuple[TreeValue, str]]], graph: Union[Graph, Digraph, None],
               configs: List[Tuple[str, str]], title: Optional[str],
               outputs: List[str], fmt: Optional[str], print_to_stdout: bool,
               dups: List[type], duplicate_all: bool):
        if graph:
            if trees or configs or title or dups or duplicate_all:
                warnings.warn(RuntimeWarning('The imported trees and related options will be '
                                             'ignored due to the enablement of -g option.'))
            g = graph
        else:
            trees = [(v, k) for k, v in OrderedDict([(k, v) for v, k in chain(*trees)]).items()]
            configs = {key: value for key, value in configs}
            title = title or f'Graph with {len(trees)} tree(s) - {", ".join(tuple([k for _, k in trees]))}.'

            g = graphics(
                *trees,
                dup_value=True if duplicate_all else tuple(dups),
                title=title, cfg=configs,
            )

        if print_to_stdout:
            if outputs:
                warnings.warn(RuntimeWarning('The output destinations in -o options '
                                             'will be ignored due to the enablement of -O option.'))
            click.echo(g.source)
        else:
            for output in outputs:
                _fmt = _save_graph_fmt_infer(output, fmt)
                with _click_pending(f'Exporting graph to {repr(output)} as format {repr(_fmt)} ... '):
                    _save_graph(g, output, _fmt)

    return cli
