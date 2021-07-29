import re
from queue import Queue

from graphviz import Digraph
from treelib import Tree as LibTree

from .random import random_hex_with_timestamp

_ROOT_ID = '_root'
_NODE_ID_TEMP = '_node_{id}'


def build_tree(root, represent=None, iterate=None, recurse=None) -> LibTree:
    represent = represent or repr
    iterate = iterate or (lambda x: x.items())
    recurse = recurse or (lambda x: hasattr(x, 'items'))

    _tree = LibTree()
    _tree.create_node(represent(root), _ROOT_ID)
    _index, _queue = 0, Queue()
    _queue.put((_ROOT_ID, root))

    while not _queue.empty():
        _parent_id, _parent_tree = _queue.get()

        for key, value in iterate(_parent_tree):
            _index += 1
            _current_id = _NODE_ID_TEMP.format(id=_index)
            _tree.create_node(
                "{key} --> {value}".format(key=repr(key), value=represent(value)),
                _current_id,
                _parent_id
            )
            if recurse(value):
                _queue.put((_current_id, value))

    return _tree


_NAME_PATTERN = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def _title_flatten(title):
    title = re.sub(r'[^a-zA-Z0-9_]+', '_', str(title))
    title = re.sub(r'_+', '_', title)
    title = title.strip('_').lower()
    return title


def build_graph(root, node_id, name=None, title=None,
                root_title=None, represent=None, iterate=None, recurse=None) -> Digraph:
    represent = represent or repr
    iterate = iterate or (lambda x: x.items())
    recurse = recurse or (lambda x: hasattr(x, 'items'))
    root_title = root_title or '<root>'

    title = title or 'untitled_' + random_hex_with_timestamp()
    name = name or _title_flatten(title)
    graph = Digraph(name=name, comment=title)
    graph.graph_attr.update({'label': title, 'bgcolor': '#ffffff00'})
    graph.node(node_id(root), label=root_title)

    _queue = Queue()
    _queue.put((node_id(root), root, []))

    while not _queue.empty():
        _parent_id, _parent_tree, _parent_path = _queue.get()

        for key, value in iterate(_parent_tree):
            _current_path = [*_parent_path, key]
            if recurse(value):
                _current_id = node_id(value)
                _current_label = '.'.join([root_title, *_current_path])
                _queue.put((_current_id, value, _current_path))
            else:
                _current_id = node_id(_parent_tree) + "__" + _title_flatten(str(key))
                _current_label = represent(value)

            graph.node(_current_id, label=_current_label)
            graph.edge(_parent_id, _current_id, label=key)

    return graph
