from functools import lru_cache
from typing import Type, Callable, Union, Optional, Tuple

from graphviz import Digraph, nohtml
from hbutils.reflection import post_process, dynamic_call, freduce

from .tree import TreeValue
from ...utils import build_graph, Color
from ...utils.tree import SUFFIXED_TAG


def _min_distance(l_, n):
    list_ = sorted(l_)
    return min([abs(a - b) for a, b in zip(list_, list_[1:] + [list_[0] + n])])


_FIRST_DIS_CNT = 2


def _dis_ratios(n, s, t):
    l_ = [(i * t + s) % n for i in range(n)]
    _dis = [_min_distance(l_[:i], n) for i in range(_FIRST_DIS_CNT, n)]
    _exp = [n // i for i in range(_FIRST_DIS_CNT, n)]
    _ratios = [e / d for d, e in zip(_dis, _exp)]
    return max(_ratios), tuple(_ratios)


@lru_cache()
def _gcd(x, y):
    if y == 0:
        return x
    else:
        return _gcd(y, x % y)


@lru_cache()
def _best_t_for_n_s(n, s):
    _final_mean, _final_t = None, None
    for _current_t in range(1, (n + 1) // 2 + 1):
        if _gcd(_current_t, n) == 1:
            _current_mean = _dis_ratios(n, s, _current_t)
            if _final_mean is None or _current_mean < _final_mean:
                _final_mean, _final_t = _current_mean, _current_t

    return n, _final_t, _final_mean


@lru_cache()
def _hue_id_mapping(n, s):
    _, t, _ = _best_t_for_n_s(n, s)
    return [(t * i + s) % n for i in range(n)]


@lru_cache()
def _base_hue(n, s, i):
    return (_hue_id_mapping(n, s)[i] + 0.5) / n


@lru_cache()
def _all_color(n, s, i):
    h = _base_hue(n, s, i)

    # line color
    _line = Color.from_hsv(h, 0.8, 0.6, alpha=0.8)

    # key font color
    _key = Color.from_hsv(h, 1.0, 0.45, alpha=1.0)

    # border color
    _border_1 = Color.from_hsv(h, 0.65, 0.7, alpha=0.6)
    _border_2 = Color.from_hsv(h, 0.65, 0.7, alpha=0.0)

    # shape color
    _shape = Color.from_hsv(h, 0.55, 1.0, alpha=0.6)

    # data font color
    _data = Color.from_hsv(h, 1.0, 0.2, alpha=1.0)

    return _line, _key, _border_1, _border_2, _shape, _data


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
    return 'node_%x' % (id(current._detach()))


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


_GENERIC_N = 36
_GENERIC_S = _GENERIC_N // 3


def graphics(*trees, title: Optional[str] = None, cfg: Optional[dict] = None,
             dup_value: Union[bool, Callable, type, Tuple[Type, ...]] = False,
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

    def _node_tag(current, parent, current_path, parent_path, is_node):
        if is_node:
            return _node_id(current, current_path)
        else:
            return dynamic_call(
                _dup_value_func(dup_value) or _default_value_id
            )(current, parent, current_path, parent_path)

    setattr(_node_tag, SUFFIXED_TAG, True)

    _line_color = lambda i: _all_color(_GENERIC_N, _GENERIC_S, i)[0]
    _key_font_color = lambda i: _all_color(_GENERIC_N, _GENERIC_S, i)[1]
    _border_color = lambda i, is_node: _all_color(_GENERIC_N, _GENERIC_S, i)[2 if is_node else 3]
    _shape_color = lambda i: _all_color(_GENERIC_N, _GENERIC_S, i)[4]
    _data_font_color = lambda i: _all_color(_GENERIC_N, _GENERIC_S, i)[5]

    return build_graph(
        *trees,
        node_id_gen=_node_tag,
        graph_title=title or "<untitled>",
        graph_cfg=cfg or {},
        repr_gen=repr_gen or (lambda x: nohtml(repr(x))),
        iter_gen=lambda n: iter(n) if isinstance(n, TreeValue) else None,
        node_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node, is_root, root: {
            'fillcolor': _shape_color(root[2]),
            'color': _border_color(root[2], is_node),
            'fontcolor': _data_font_color(root[2]),
            'style': 'filled',
            'shape': 'diamond' if is_root else ('ellipse' if is_node else 'box'),
            'penwidth': 3 if is_root else 1.5,
            'fontname': "Times-Roman bold" if is_node else "Times-Roman",
        }, (node_cfg_gen or (lambda: {}))),
        edge_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node, root: {
            'arrowhead': 'vee' if is_node else 'dot',
            'arrowsize': 1.0 if is_node else 0.5,
            'color': _line_color(root[2]),
            'fontcolor': _key_font_color(root[2]),
            'fontname': "Times-Roman bold",
        }, (edge_cfg_gen or (lambda: {}))),
    )
