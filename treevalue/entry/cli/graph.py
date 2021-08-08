import codecs
import glob
import os
import pickle
import shutil
import tempfile
import warnings
from functools import partial
from itertools import chain
from string import Template
from typing import Tuple, List, Optional, Iterator, Union

import click
import dill
from graphviz import Digraph, Graph

from .base import CONTEXT_SETTINGS
from .utils import _multiple_validator, _click_pending, _exception_validation, _wrap_validator
from ...tree import TreeValue, load, graphics
from ...utils import dynamic_call, quick_import_object, iter_import_objects


@dynamic_call
def _import_tree_from_package(obj_pattern, title=None) -> Iterator[Tuple[TreeValue, str]]:
    _title_template = Template(title or '$name')
    for _object, _module, _name in iter_import_objects(obj_pattern):
        _title = _title_template.safe_substitute(dict(module=_module, name=_name))
        if isinstance(_object, TreeValue):
            yield _object, _title


@dynamic_call
def _import_tree_from_binary(filename_pattern, title='') -> Iterator[Tuple[TreeValue, str]]:
    _title_template = Template(title or '$bodyname')
    for filename in glob.glob(filename_pattern):
        if not os.path.exists(filename) or not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            continue

        filename = os.path.abspath(filename)
        _name_body, _name_ext = os.path.splitext(os.path.basename(filename))
        _name_ext = _name_ext[1:] if _name_ext.startswith('.') else _name_ext
        with open(filename, 'rb') as file:
            try:
                yield load(file), _title_template.safe_substitute(dict(
                    fullname=filename,
                    dirname=os.path.dirname(filename),
                    basename=os.path.basename(filename),
                    extname=_name_ext,
                    bodyname=_name_body,
                ))
            except (pickle.UnpicklingError, dill.UnpicklingError, EOFError, IOError):
                continue


@_multiple_validator
def validate_trees(value: str) -> Iterator[Tuple[TreeValue, str]]:
    _items = [item.strip() for item in value.split(':', maxsplit=3)]
    return chain(_import_tree_from_binary(*_items), _import_tree_from_package(*_items))


@_exception_validation
@_wrap_validator
def validate_graph(value: str):
    if value is None:
        return value

    _graph, _module, _name = quick_import_object(value)
    if not isinstance(_graph, (Graph, Digraph)):
        raise TypeError(f'Graphviz dot expected but {repr(type(_graph).__name__)} found.')
    else:
        return _graph


@_multiple_validator
def validate_cfg(value: str) -> Tuple[str, str]:
    _items = value.split('=', maxsplit=2)
    if len(_items) < 2:
        raise click.BadParameter(f'Configuration should be KEY=VALUE, but {repr(value)} found.')

    key, value = _items
    return key, value


@_multiple_validator
def validate_duplicate_types(value: str):
    _it, _module, _name = quick_import_object(value)
    if not isinstance(_it, type):
        raise TypeError(f'Python type expected but {repr(type(_it).__name__)} found.')
    else:
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
                  help='Graph to be exported, -t options will be ignored.')
    @click.option('-c', '--config', 'configs', type=click.UNPROCESSED, callback=validate_cfg,
                  multiple=True, help='External configuration when generating graph. '
                                      'Like \'-c bgcolor=#ffffff00\', will be displayed as '
                                      'graph [bgcolor=#ffffff00] in source code. ')
    @click.option('-T', '--title', type=str, default=None,
                  help='Title of the graph.')
    @click.option('-o', '--output', 'outputs', type=click.types.Path(dir_okay=False),
                  multiple=True, help='Output file path, multiple output is supported.')
    @click.option('-O', '--stdout', 'print_to_stdout', is_flag=True, default=False,
                  help='Directly print graphviz source code to stdout.', show_default=True)
    @click.option('-F', '--format', 'fmt', type=str, required=False,
                  help='Format of output file.')
    @click.option('-d', '--duplicate', 'dups', type=click.UNPROCESSED, callback=validate_duplicate_types,
                  multiple=True, help='The types need to be duplicated, '
                                      'such as \'-d numpy.ndarray\', \'-d torch.Tensor\' and '
                                      '\'-d set\'.')
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
            _tree_mapping, _names, _name_set = {}, [], set()
            for v, k in chain(*trees):
                if k not in _name_set:
                    _name_set.add(k)
                    _names.append(k)
                _tree_mapping[k] = v

            trees = [(_tree_mapping[k], k) for k in _names]
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
