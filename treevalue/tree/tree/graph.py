import colorsys
from functools import wraps
from typing import Type

from graphviz import Digraph

from .tree import TreeValue, get_data_property
from ...utils import get_class_full_name, seed_random, post_process, build_graph, dynamic_call

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


@_rgb_str_wrap
@_rrgb_wrap
def _color_from_class_raw(type_: Type[TreeValue], alpha=None):
    with seed_random(_str_hash(get_class_full_name(type_))) as rnd:
        h, s, v = rnd.random(), rnd.random() * 0.4 + 0.6, rnd.random() * 0.4 + 0.6
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        if alpha is None:
            return r, g, b
        else:
            return r, g, b, alpha


_color_from_class = post_process(lambda s: '#%s' % (s,))(_color_from_class_raw)


def _color_from_node(n, alpha=None):
    return _color_from_class(type(n), alpha)


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


def graphics(*trees, title=None, cfg=None, repr_gen=None,
             node_cfg_gen=None, edge_cfg_gen=None) -> Digraph:
    return build_graph(
        *trees,
        node_id_gen=lambda n: 'node_%x' % (id(get_data_property(n).actual())),
        graph_title=title or "<untitled>",
        graph_cfg=cfg or {},
        repr_gen=repr_gen or (lambda x: repr(x)),
        iter_gen=lambda n: iter(n) if isinstance(n, TreeValue) else None,
        node_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node, is_root: {
            'fillcolor': _color_from_node(n if is_node else p, 0.5),
            'color': _color_from_node(n if is_node else p, 0.7 if is_node else 0.0),
            'style': 'filled',
            'shape': 'diamond' if is_root else ('ellipse' if is_node else 'box'),
            'penwidth': 3 if is_root else 1.5,
            'fontname': "Times-Roman bold" if is_node else "Times-Roman",
        }, (node_cfg_gen or (lambda: {}))),
        edge_cfg_gen=_dict_call_merge(lambda n, p, np, pp, is_node: {
            'arrowhead': 'vee' if is_node else 'dot',
            'arrowsize': 1.0 if is_node else 0.5,
            'color': _color_from_node(n if is_node else p, 0.7 if is_node else 0.9),
            'fontcolor': _color_from_node(n if is_node else p, 1.0),
            'fontname': "Times-Roman",
        }, (edge_cfg_gen or (lambda: {}))),
    )
