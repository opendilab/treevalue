import colorsys
from enum import IntEnum, unique
from functools import wraps
from typing import Type, Callable, Union, Optional, Tuple, Any

import enum_tools
from graphviz import Digraph

from .tree import TreeValue, get_data_property
from ...utils import get_class_full_name, seed_random, post_process, build_graph, dynamic_call, \
    int_enum_loads, freduce
from ...utils.tree import SUFFIXED_TAG

_PRIME_P, _PRIME_Q, _PRIME_R, _PRIME_S = 482480892821, 697797055633, 251526220339, 572076910547


def _str_hash(string):
    sum_ = 0
    for ch in str(string):
        sum_ = (sum_ + ord(ch) * _PRIME_P) % _PRIME_Q
    return sum_


_MAX_RGB = 0xff


def _max_mul(r):
    return int(round(r * _MAX_RGB))


def _rrgb_wrap(func):
    @wraps(func)
    def _new_func(*args, **kwargs):
        _result = func(*args, **kwargs)
        if len(_result) > 3:
            r, g, b, a = _result[:4]
            return _max_mul(r), _max_mul(g), _max_mul(b), _max_mul(a)
        else:
            r, g, b = _result[:3]
            return _max_mul(r), _max_mul(g), _max_mul(b)

    return _new_func


def _rgb_str_wrap(func):
    @wraps(func)
    def _new_func(*args, **kwargs):
        _result = func(*args, **kwargs)
        if len(_result) > 3:
            return '%02x%02x%02x%02x' % tuple(_result[:4])
        else:
            return '%02x%02x%02x' % tuple(_result[:3])

    return _new_func


_H_CLUSTERS = 18
_H_UNIT = 1 / _H_CLUSTERS
_H_MIN = 0
_H_MAX = _H_CLUSTERS - 1
_H_CLUSTER_MAPPING = [11, 8, 7, 4, 16, 0, 13, 6, 14, 3, 15, 2, 17, 1, 12, 9, 10, 5]

_S_CLUSTERS = 12
_S_UNIT = 1 / _S_CLUSTERS
_S_MIN = 6
_S_MAX = 9


@post_process(lambda s: '#%s' % (s,))
@_rgb_str_wrap
@_rrgb_wrap
def _color_from_tag(tag: str, alpha=None, hx: int = None, sr: float = None):
    if not isinstance(tag, str):
        tag = 'hash_%x' % (hash(tag),)

    with seed_random(_str_hash(tag)) as rnd:
        h, s, v = _H_CLUSTER_MAPPING[rnd.randint(_H_MIN, _H_MAX)] * _H_UNIT, \
                  rnd.randint(_S_MIN, _S_MAX) * _S_UNIT, rnd.random() * 0.12 + 0.88
        if hx is not None:
            h = _H_CLUSTER_MAPPING[hx % _H_CLUSTERS] * _H_UNIT
        if sr is not None:
            s = max(0.0, min(1.0, sr))

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        if alpha is None:
            return r, g, b
        else:
            return r, g, b, alpha


def _color_from_data(data, alpha=None, is_edge: bool = False):
    if isinstance(data, tuple):
        hx, tag = data
        return _color_from_tag(tag, alpha, hx)
    else:
        return _color_from_tag(data, alpha, None)


@enum_tools.documentation.document_enum
@int_enum_loads(name_preprocess=str.upper)
@unique
class ColorTheme(IntEnum):
    TYPE = 1  # doc: Distinct colors by the tree types
    INDEX = 2  # doc: Distinct colors by the index of the argument tree
    NAME = 3  # doc: Distinct colors by the index of the argument's name

    @dynamic_call
    def __call__(self, root_node, root_title: str, root_index: int):
        if self == self.__class__.TYPE:
            return get_class_full_name(type(root_node))
        elif self == self.__class__.INDEX:
            return root_index, 'root_%d' % (root_index,)
        elif self == self.__class__.NAME:
            return 'title_%x' % (_str_hash(root_title),)


@freduce(init=lambda: (lambda: {}))
def _dict_call_merge(d1, d2):
    d1 = dynamic_call(d1)
    d2 = dynamic_call(d2)

    def _new_func(*args, **kwargs):
        _r1 = d1(*args, **kwargs)
        _r2 = d2(*args, **kwargs)

        _return = dict(_r1)
        _return.update(_r2)
        return _return

    return _new_func


@dynamic_call
def _node_id(current):
    return 'node_%x' % (id(get_data_property(current).actual()))


@dynamic_call
def _default_value_id(_, parent, current_path, parent_path):
    return 'value__%s__%s' % (_node_id(parent, parent_path), current_path[-1])


@post_process(lambda f: dynamic_call(f) if f is not None else None)
def _dup_value_func(dup_value):
    if dup_value:
        if isinstance(dup_value, (type, tuple)):
            _dup_value = lambda v: id(v) if isinstance(v, dup_value) else None
        elif hasattr(dup_value, '__call__'):
            _dup_value = dup_value
        else:
            _dup_value = lambda v: id(v)
        _id_getter = dynamic_call(_dup_value)

        def _new_func(current, parent, current_path, parent_path):
            _id = _id_getter(current, parent, current_path, parent_path)
            if not _id:
                return _default_value_id(current, parent, current_path, parent_path)
            elif isinstance(_id, int):
                return 'value_%x' % (_id,)
            else:
                return 'value_%s' % (_id,)

        return _new_func
    else:
        return None


def graphics(*trees, title: Optional[str] = None, cfg: Optional[dict] = None,
             dup_value: Union[bool, Callable, type, Tuple[Type, ...]] = False,
             color_theme_gen: Union[Callable, str, ColorTheme, Any, None] = None,
             repr_gen: Optional[Callable] = None,
             node_cfg_gen: Optional[Callable] = None,
             edge_cfg_gen: Optional[Callable] = None) -> Digraph:
    """
    Overview:
        Draw graph by tree values.
        Multiple tree values is supported.

    Args:
        - trees: Given tree values, tuples of `Tuple[TreeValue, str]` or tree values are both accepted.
        - title (:obj:`Optional[str]`): Title of the graph.
        - cfg (:obj:`Optional[dict]`): Configuration of the graph.
        - dup_value (:obj:`Union[bool, Callable, type, Tuple[Type, ...]]`): Value duplicator, \
            set `True` to make value with same id use the same node in graph, \
            you can also define your own node id algorithm by this argument. \
            Default is `False` which means do not use value duplicator.
        - repr_gen (:obj:`Optional[Callable]`): Representation format generator, \
            default is `None` which means using `repr` function.
        - node_cfg_gen (:obj:`Optional[Callable]`): Node configuration generator, \
            default is `None` which means no configuration.
        - edge_cfg_gen (:obj:`Optional[Callable]`): Edge configuration generator, \
            default is `None` which means no configuration.

    Returns:
        - graph (:obj:`Digraph`): Generated graph of tree values.
    """

    color_theme_gen = color_theme_gen or ColorTheme.TYPE
    if not hasattr(color_theme_gen, '__call__'):
        color_theme_gen = ColorTheme.loads(color_theme_gen)
    color_theme_gen = post_process(lambda x: '%x' % _str_hash(x))(dynamic_call(color_theme_gen))

    def _node_tag(current, parent, current_path, parent_path, is_node):
        if is_node:
            return _node_id(current, current_path)
        else:
            return dynamic_call(
                _dup_value_func(dup_value) or _default_value_id
            )(current, parent, current_path, parent_path)

    setattr(_node_tag, SUFFIXED_TAG, True)

    return build_graph(
        *trees,
        node_id_gen=_node_tag,
        graph_title=title or "<untitled>",
        graph_cfg=cfg or {},
        repr_gen=repr_gen or (lambda x: repr(x)),
        iter_gen=lambda n: iter(n) if isinstance(n, TreeValue) else None,
        node_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node, is_root, root: {
            'fillcolor': _color_from_data(color_theme_gen(*root), 0.5),
            'color': _color_from_data(color_theme_gen(*root), 0.7 if is_node else 0.0),
            'style': 'filled',
            'shape': 'diamond' if is_root else ('ellipse' if is_node else 'box'),
            'penwidth': 3 if is_root else 1.5,
            'fontname': "Times-Roman bold" if is_node else "Times-Roman",
        }, (node_cfg_gen or (lambda: {}))),
        edge_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node, root: {
            'arrowhead': 'vee' if is_node else 'dot',
            'arrowsize': 1.0 if is_node else 0.5,
            'color': _color_from_data(color_theme_gen(*root), 0.7 if is_node else 0.9),
            'fontcolor': _color_from_data(color_theme_gen(*root), 1.0),
            'fontname': "Times-Roman bold",
        }, (edge_cfg_gen or (lambda: {}))),
    )
