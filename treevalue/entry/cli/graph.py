import codecs
import importlib
import os
import pickle
import shutil
import tempfile
from functools import partial
from itertools import chain
from string import Template
from typing import Tuple, List, Optional

import click
import dill
from graphviz import Digraph

from .base import CONTEXT_SETTINGS
from .utils import _multiple_validator, _EXPECTED_TREE_ERRORS
from ...tree import TreeValue, load, graphics
from ...utils import dynamic_call, post_process


def _title_check(result):
    _tree, _title = result
    if not _title:
        raise ValueError(f'Title expected non-empty value but {repr(_title)} found.')

    return _tree, _title


@dynamic_call
@post_process(_title_check)
def _import_tree_from_package(package_name, name, title=None):
    if not name:
        raise ValueError(f'Tree\'s name not provided for {repr(package_name)}.')

    title = title or name
    package = importlib.import_module(package_name)
    _object = getattr(package, name)
    if isinstance(_object, TreeValue):
        return _object, title
    else:
        raise TypeError(f'TreeValue object expected, but {repr(_object)} found')


@dynamic_call
@post_process(_title_check)
def _import_tree_from_binary(binary_file_name, title=''):
    if not title:
        raise ValueError(f'Binary-based tree \'s title not provided for {repr(binary_file_name)}.')

    if not os.path.exists(binary_file_name):
        raise FileNotFoundError(f'File {repr(binary_file_name)} not found.')
    elif not os.path.isfile(binary_file_name):
        raise IsADirectoryError(f'File {repr(binary_file_name)} is not a file.')
    elif not os.access(binary_file_name, os.R_OK):
        raise PermissionError(f'File {repr(binary_file_name)} is not readable.')
    else:
        with open(binary_file_name, 'rb') as file:
            try:
                return load(file), title
            except (pickle.UnpicklingError, dill.UnpicklingError):
                raise TypeError(f'File {repr(binary_file_name)} is not a binary-based tree file.')


@_multiple_validator
def validate_trees(value: str) -> Tuple[TreeValue, str]:
    _items = [item.strip() for item in value.split(':', maxsplit=3)]
    try:
        _tree, _title = _import_tree_from_package(*_items)
    except _EXPECTED_TREE_ERRORS:
        _tree, _title = _import_tree_from_binary(*_items)

    return _tree, _title


_DEFAULT_TEMPLATE_STR = '$name'
_DEFAULT_INCLUDED_ITEMS = lambda x: {key: value for key, value in x.__dict__.items() if isinstance(value, TreeValue)}


@_multiple_validator
def validate_tree_scripts(value: str) -> List[Tuple[TreeValue, str]]:
    _items = value.split(':', maxsplit=3)
    if len(_items) == 1:
        _name_template = _DEFAULT_TEMPLATE_STR
        _included_items = _DEFAULT_INCLUDED_ITEMS
    elif len(_items) == 2:
        _name_template = _items[1]
        _included_items = _DEFAULT_INCLUDED_ITEMS
    else:
        _name_template = _items[1]
        included_names = {item.strip() for item in _items[2].split(',')}
        _included_items = lambda x: {k: v for k, v in _DEFAULT_INCLUDED_ITEMS(x).items() if k in included_names}

    package = importlib.import_module(_items[0])
    items = _included_items(package)
    template = Template(_name_template or _DEFAULT_TEMPLATE_STR)

    return [(v, template.safe_substitute(dict(name=k))) for k, v in items.items()]


@_multiple_validator
def validate_cfg(value: str) -> Tuple[str, str]:
    _items = value.split('=', maxsplit=2)
    if len(_items) < 2:
        raise click.BadParameter(f'Configuation should be KEY=VALUE, but {repr(value)} found.')

    key, value = _items
    return key, value


@_multiple_validator
def validate_duplicate_types(value: str):
    _items = [item[::-1] for item in value[::-1].split('.', maxsplit=2)][::-1]
    if len(_items) == 2:
        _package_name, _obj_name = _items
    else:
        _package_name, _obj_name = None, value

    package = importlib.import_module(_package_name or 'builtins')
    _it = getattr(package, _obj_name)
    if not isinstance(_it, type):
        raise TypeError(f'Python type expected but {repr(type(_it).__name__)} found.')

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


def _save_graph(g: Digraph, path: str, fmt: Optional[str] = None):
    path = os.path.abspath(path)
    if not fmt:
        _basename, _extname = os.path.splitext(path)
        if _extname:
            fmt = _extname[1:]

    _saver = partial(_save_image, fmt=fmt) if fmt in _IMAGE_FMTS else _save_source_code
    return _saver(g, path)


def _graph_cli(cli: click.Group):
    @cli.command('graph', help='Generate graph by trees and graphviz elements.',
                 context_settings=CONTEXT_SETTINGS)
    @click.option('-t', '--tree', 'trees', type=click.UNPROCESSED, callback=validate_trees,
                  multiple=True, help='Trees to be imported.')
    @click.option('-s', '--tree-script', 'ts', type=click.UNPROCESSED, callback=validate_tree_scripts,
                  multiple=True, help='Tree scripts to be imported.')
    @click.option('-c', '--config', 'configs', type=click.UNPROCESSED, callback=validate_cfg,
                  multiple=True, help='External configuration when generating graph. '
                                      'Like \'-c bgcolor=#ffffff00\', will be displayed as '
                                      'graph [bgcolor=#ffffff00] in source code. ')
    @click.option('-T', '--title', type=str, default='<untitled>',
                  help='Title of the graph.', show_default=True)
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
    def _graph(trees, ts, configs: List[Tuple[str, str]], title: Optional[str],
               outputs: List[str], fmt: Optional[str], print_to_stdout: bool,
               dups: List[type], duplicate_all: bool):
        _tree_mapping, _names, _name_set = {}, [], set()
        for v, k in chain(*ts, trees):
            if k not in _name_set:
                _name_set.add(k)
                _names.append(k)
            _tree_mapping[k] = v

        trees = [(_tree_mapping[k], k) for k in _names]
        configs = {key: value for key, value in configs}

        g = graphics(
            *trees,
            dup_value=True if duplicate_all else tuple(dups),
            title=title, cfg=configs,
        )

        if print_to_stdout:
            click.echo(g.source)
        for output in outputs:
            _save_graph(g, output, fmt)

    return cli
