import re
from functools import wraps
from queue import Queue
from typing import Optional, Mapping, Any, Callable

from graphviz import Digraph
from hbutils.reflection import dynamic_call, post_process

from .random import random_hex_with_timestamp


def _title_flatten(title):
    title = re.sub(r'[^a-zA-Z0-9_]+', '_', str(title))
    title = re.sub(r'_+', '_', title)
    title = title.strip('_').lower()
    return title


def _no_none_value(dict_) -> dict:
    return type(dict_)({key: value for key, value in dict_.items() if value is not None})


def _cfg_func_wrap(func):
    @wraps(func)
    @post_process(lambda d: type(d)({str(key): str(value) for key, value in d.items()}))
    @post_process(_no_none_value)
    def _new_func(*args, **kwargs):
        return func(*args, **kwargs)

    return _new_func


SUFFIXED_TAG = '__suffixed__'


def suffixed_node_id(func):
    if getattr(func, SUFFIXED_TAG, None):
        return func

    func = dynamic_call(func)

    @wraps(func)
    @dynamic_call
    def _new_func(current, parent, current_path, parent_path, is_node):
        if is_node:
            return func(current, current_path)
        else:
            return '%s__%s' % (func(parent, parent_path), current_path[-1])

    setattr(_new_func, SUFFIXED_TAG, True)
    return _new_func


@suffixed_node_id
@dynamic_call
def _default_node_id(current):
    return 'node_%x' % (id(current),)


def _root_process(root, index):
    if isinstance(root, tuple):
        if len(root) < 1:
            return None
        elif len(root) == 1:
            return _root_process(root[0], index)
        else:
            return root[0], str(root[1]), index
    else:
        return root, '<root_%d>' % (index,), index


def build_graph(*roots, node_id_gen: Optional[Callable] = None,
                graph_title: Optional[str] = None, graph_name: Optional[str] = None,
                graph_cfg: Optional[Mapping[str, Any]] = None,
                repr_gen: Optional[Callable] = None, iter_gen: Optional[Callable] = None,
                node_cfg_gen: Optional[Callable] = None, edge_cfg_gen: Optional[Callable] = None) -> Digraph:
    """
    Overview:
        Build a graphviz graph based on given tree structure.

    Arguments:
        - roots: Root nodes of the graph.
        - node_id_gen (:obj:`Optional[Callable]`): Node id generation function, \
            default is `None` which means based on object id.
        - graph_title (:obj:`Optional[str]`): Title of the graph, \
            default is `None` which means generate automatically based on timestamp.
        - graph_name (:obj:`Optional[str]`): Name of the graph, \
            default is `None` which means auto generated based on graph title.
        - graph_cfg (:obj:`Optional[Mapping[str, Any]]`): Configuration of graph, \
            default is `None` which means no configuration.
        - repr_gen (:obj:`Optional[Callable]`): Representation format generator, \
            default is `None` which means using `repr` function.
        - iter_gen (:obj:`Optional[Callable]`): Iterator generator, \
            default is `None` which means load from `items` method.
        - node_cfg_gen (:obj:`Optional[Callable]`): Node configuration generator, \
            default is `None` which means no configuration.
        - edge_cfg_gen (:obj:`Optional[Callable]`): Edge configuration generator, \
            default is `None` which means no configuration.

    Returns:
        - dot (:obj:`Digraph`): Graphviz directed graph object.
    """
    roots = [_root_process(root, index) for index, root in enumerate(roots)]
    roots = [item for item in roots if item is not None]

    node_id_gen = dynamic_call(suffixed_node_id(node_id_gen or _default_node_id))
    graph_title = graph_title or ('untitled_' + random_hex_with_timestamp())
    graph_name = graph_name or _title_flatten(graph_title)
    graph_cfg = _no_none_value(graph_cfg or {})

    repr_gen = dynamic_call(repr_gen or repr)
    iter_gen = dynamic_call(iter_gen or (lambda x: x.items() if hasattr(x, 'items') else None))
    node_cfg_gen = _cfg_func_wrap(dynamic_call(node_cfg_gen or (lambda: {})))
    edge_cfg_gen = _cfg_func_wrap(dynamic_call(edge_cfg_gen or (lambda: {})))

    graph = Digraph(name=graph_name, comment=graph_title)
    graph.graph_attr.update(graph_cfg or {})
    graph.graph_attr.update({'label': graph_title})

    _queue = Queue()
    _queued_node_ids = set()
    _queued_edges = set()
    for root_info in roots:
        root, root_title, root_index = root_info
        root_node_id = node_id_gen(root, None, [], [], True)
        if root_node_id not in _queued_node_ids:
            graph.node(
                name=root_node_id, label=root_title,
                **node_cfg_gen(root, None, [], [], True, True, root_info)
            )
            _queue.put((root_node_id, root, (root, root_title, root_index), []))
            _queued_node_ids.add(root_node_id)

    while not _queue.empty():
        _parent_id, _parent_node, _root_info, _parent_path = _queue.get()
        _root_node, _root_title, _root_index = _root_info

        for key, _current_node in iter_gen(_parent_node, _parent_path):
            _current_path = [*_parent_path, key]
            _is_node = not not iter_gen(_current_node, _current_path)
            _current_id = node_id_gen(_current_node, _parent_node, _current_path, _parent_path, _is_node)
            if iter_gen(_current_node, _current_path):
                _current_label = '.'.join([_root_title, *_current_path])
            else:
                _current_label = repr_gen(_current_node, _current_path)

            if _current_id not in _queued_node_ids:
                graph.node(_current_id, label=_current_label,
                           **node_cfg_gen(_current_node, _parent_node, _current_path, _parent_path,
                                          _is_node, False, _root_info))
                if iter_gen(_current_node, _current_path):
                    _queue.put((_current_id, _current_node, _root_info, _current_path))
                _queued_node_ids.add(_current_id)
            if (_parent_id, _current_id, key) not in _queued_edges:
                graph.edge(_parent_id, _current_id, label=key,
                           **edge_cfg_gen(_current_node, _parent_node, _current_path, _parent_path,
                                          _is_node, _root_info))
                _queued_edges.add((_parent_id, _current_id, key))

    return graph
