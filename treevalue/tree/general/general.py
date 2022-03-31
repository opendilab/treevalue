from functools import lru_cache
from functools import wraps, partial
from typing import Mapping, Optional, Any, Type, TypeVar, Union, Callable, Tuple

from graphviz import Digraph
from hbutils.reflection import dynamic_call, raising

from ..func import method_treelize, MISSING_NOT_ALLOW, func_treelize
from ..tree import TreeValue, jsonify, clone, typetrans, mapping, mask, filter_, reduce_, union, graphics, walk
from ..tree import rise as rise_func
from ..tree import subside as subside_func

_BASE_GENERATION_CONFIG = {}


def general_tree_value(base: Optional[Mapping[str, Any]] = None,
                       methods: Optional[Mapping[str, Any]] = None):
    """
    Overview:
        Get general tree value class.

    Arguments:
        - base (:obj:`Optional[Mapping[str, Any]]`): Base configuration of `func_treelize`.
        - methods (:obj:`Optional[Mapping[str, Any]]`): Method configurations of `func_treelize`.

    Returns:
        - clazz (:obj:`Type[TreeValue]`): General tree value class.
    """
    base = base or {}
    methods = methods or {}

    def _dynamic_suffix_dec(func, f):
        return wraps(func)(dynamic_call(f))

    @lru_cache()
    def _get_decorator(name, treelize: bool, ext_cfg: Optional[tuple] = None):
        _item = methods.get(name, None)

        if treelize and isinstance(_item or {}, dict):
            _config = _BASE_GENERATION_CONFIG.copy()
            _config.update(base)
            _config.update(_item or {})
            _config.update(dict(ext_cfg or ()))
            return lambda func: method_treelize(**_config)(func)
        elif isinstance(_item, BaseException) or (isinstance(_item, type) and issubclass(_item, BaseException)):
            return lambda func: _dynamic_suffix_dec(func, raising(_item))
        elif hasattr(_item, '__call__'):
            return lambda func: _dynamic_suffix_dec(func, _item)
        elif name in methods.keys():
            return lambda func: _dynamic_suffix_dec(func, lambda: methods[name])
        else:
            return lambda func: func

    def _decorate(func, treelize: bool, ext_cfg: Optional[dict] = None):
        return _get_decorator(func.__name__, treelize, tuple(sorted((ext_cfg or {}).items())))(func)

    _decorate_treelize = partial(_decorate, treelize=True)
    _decorate_method = partial(_decorate, treelize=False)
    _decorate_and_replace = partial(_decorate, treelize=True, ext_cfg=dict(self_copy=True))

    _TreeValue = TypeVar("_TreeValue", bound=TreeValue)

    # noinspection PyUnresolvedReferences,PyMethodFirstArgAssignment
    class _GeneralTreeValue(TreeValue):
        @method_treelize()
        def _attr_extern(self, key):
            """
            Overview:
                External protected function for support the unfounded attributes. \
                In `FastTreeValue` it is extended to support the access to values' attribute.

            Arguments:
                - key (:obj:`str`): Attribute name.

            Returns:
                - return (:obj:): TreeValue of the values' attribute.

            Example:
                >>> class Container:
                >>>     def __init__(self, value):
                >>>         self.__value = value
                >>>
                >>>     @property
                >>>     def value(self):
                >>>         return self.__value
                >>>
                >>>     def append(self, v):
                >>>         return self.__value + v
                >>>
                >>> t = FastTreeValue({'a': Container(1), 'b': Container(2)})
                >>> t.value   # FastTreeValue({'a': 1, 'b': 2})
                >>> t.append  # FastTreeValue({'a': <method 'append' of Container(1)>, 'b': <method 'append' of Container(2)>})
            """
            return getattr(self, key)

        @_decorate_method
        def json(self):
            """
            Overview:
                Dump current `TreeValue` object to json data.

            Returns:
                - json (:obj:`dict`): Dumped json data.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.json()  # {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
            """
            return jsonify(self)

        @_decorate_method
        def clone(self, copy_value: Union[None, bool, Callable, Any] = None):
            """
            Overview:
                Create a fully clone of the current tree.

            Returns:
                - tree (:obj:`_TreeValue`): Cloned tree value object.
                - copy_value (:obj:`Union[None, bool, Callable, Any]`): Deep copy value or not, \
                    default is `None` which means do not deep copy the values. \
                    If deep copy is required, just set it to `True`.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.x.clone()  # FastTreeValue({'c': 3, 'd': 4})
            """
            return clone(self, copy_value)

        @_decorate_method
        def type(self, clazz: Type[_TreeValue]) -> _TreeValue:
            """
            Overview:
                Transform tree value object to another tree value type. \
                Attention that in this function, no copy will be made, \
                the original tree value and the transformed tree value are using the same space area.

            Arguments:
                - return_type (:obj:`Type[_TreeValue]`): Target tree value type

            Returns:
                - tree (:obj:`_TreeValue`): Transformed tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.type(TreeValue)  # TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            """
            return typetrans(self, clazz)

        @_decorate_method
        def map(self, mapper, delayed=False):
            """
            Overview:
                Do mapping on every value in this tree.

            Arguments:
                - func (:obj:): Function for mapping
                - delayed (:obj:`bool`): Enable delayed mode for this mapping.

            Returns:
                - tree (:obj:`_TreeValue`): Mapped tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.map(lambda x: x + 2)  # FastTreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
                >>> t.map(lambda: 1)        # FastTreeValue({'a': 1, 'b': 1, 'x': {'c': 1, 'd': 1}})
                >>> t.map(lambda x, p: p)   # FastTreeValue({'a': ('a',), 'b': ('b',), 'x': {'c': ('x', 'c'), 'd': ('x', 'd')}})
            """
            return mapping(self, mapper, delayed)

        @_decorate_method
        def mask(self, mask_: TreeValue, remove_empty: bool = True):
            """
            Overview:
                Filter the element in the tree with a mask

            Arguments:
                - `mask_` (:obj:`TreeValue`): Tree value mask object
                - `remove_empty` (:obj:`bool`): Remove empty tree node automatically, default is `True`.

            Returns:
                - tree (:obj:`_TreeValue`): Filtered tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.mask(TreeValue({'a': True, 'b': False, 'x': False}))                    # FastTreeValue({'a': 1})
                >>> t.mask(TreeValue({'a': True, 'b': False, 'x': {'c': True, 'd': False}}))  # FastTreeValue({'a': 1, 'x': {'c': 3}})
            """
            return mask(self, mask_, remove_empty)

        @_decorate_method
        def filter(self, func, remove_empty: bool = True):
            """
            Overview:
                Filter the element in the tree with a predict function.

            Arguments:
                - func (:obj:): Function for filtering
                - remove_empty (:obj:`bool`): Remove empty tree node automatically, default is `True`.

            Returns:
                - tree (:obj:`_TreeValue`): Filtered tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.filter(lambda x: x < 3)                  # FastTreeValue({'a': 1, 'b': 2})
                >>> t.filter(lambda x: x < 3, False)           # FastTreeValue({'a': 1, 'b': 2, 'x': {}})
                >>> t.filter(lambda x: x % 2 == 1)             # FastTreeValue({'a': 1, 'x': {'c': 3}})
                >>> t.filter(lambda x, p: p[0] in {'b', 'x'})  # FastTreeValue({'b': 2, 'x': {'c': 3, 'd': 4}})
            """
            return filter_(self, func, remove_empty)

        @_decorate_method
        def walk(self):
            """
            Overview:
                Walk the values and nodes in the tree.
                The order of walk is not promised, if you need the ordered walking result, \
                just use function ``sorted`` at the outer side of :func:`walk`.

            Returns:
                - iter: Iterator to walk the given tree, contains 2 items, the 1st one is the full \
                    path of the node, the 2nd one is the value.

            Examples::
                >>> from treevalue import FastTreeValue, walk
                >>> tv1 = FastTreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 2}})
                >>> for k, v in tv1.walk():
                ...     print(k, v)
                () <FastTreeValue 0x7f672fc533c8>
                ├── 'a' --> 1
                ├── 'b' --> 2
                └── 'c' --> <FastTreeValue 0x7f672fc53438>
                    ├── 'x' --> 2
                    └── 'y' --> 2
                ('a',) 1
                ('b',) 2
                ('c',) <FastTreeValue 0x7f672fc53438>
                ├── 'x' --> 2
                └── 'y' --> 2
                ('c', 'x') 2
                ('c', 'y') 2
            """
            return walk(self)

        @_decorate_method
        def reduce(self, func):
            """
            Overview
                Reduce the tree to value.

            Arguments:
                - func (:obj:): Function for reducing

            Returns:
                - result (:obj:): Reduce result

            Examples:
                >>> from functools import reduce
                >>>
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.reduce(lambda **kwargs: sum(kwargs.values()))  # 10, 1 + 2 + (3 + 4)
                >>> t.reduce(lambda **kwargs: reduce(lambda x, y: x * y, list(kwargs.values())))  # 24, 1 * 2 * (3 * 4)
            """
            return reduce_(self, func)

        @_decorate_method
        def rise(self, dict_: bool = True, list_: bool = True, tuple_: bool = True, template=None):
            """
            Overview:
                Make the structure (dict, list, tuple) in value rise up to the top, above the tree value.

            Arguments:
                - `dict_` (:obj:`bool`): Enable dict rise, default is `True`.
                - `list_` (:obj:`bool`): Enable list rise, default is `True`.
                - `tuple_` (:obj:`bool`): Enable list rise, default is `True`.
                - template (:obj:): Rising template, default is `None`, which means auto detect.

            Returns:
                - risen (:obj:): Risen value.

            Example:
                >>> t = FastTreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6, 7], 'b': [7, 8]})})
                >>> dt = t.rise()
                >>> # dt will be {'a': <FastTreeValue 1>, 'b': [<FastTreeValue 2>, <FastTreeValue 3>]}
                >>> # FastTreeValue 1 will be FastTreeValue({'x': [1, 2], 'y': [5, 6, 7]})
                >>> # FastTreeValue 2 will be FastTreeValue({'x': 2, 'y': 7})
                >>> # FastTreeValue 3 will be FastTreeValue({'x': 3, 'y': 8})
                >>>
                >>> t2 = FastTreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6], 'b': [7, 8]})})
                >>> dt2 = t2.rise()
                >>> # dt2 will be {'a': [<FastTreeValue 1>, <FastTreeValue 2>], 'b': [<FastTreeValue 3>, <FastTreeValue 4>]}
                >>> # FastTreeValue 1 will be FastTreeValue({'x': 1, 'y': 5})
                >>> # FastTreeValue 2 will be FastTreeValue({'x': 2, 'y': 6})
                >>> # FastTreeValue 3 will be FastTreeValue({'x': 2, 'y': 7})
                >>> # FastTreeValue 4 will be FastTreeValue({'x': 3, 'y': 8})
                >>>
                >>> dt3 = t2.rise(template={'a': None, 'b': None})
                >>> # dt3 will be {'a': <FastTreeValue 1>, 'b': <FastTreeValue 2>}
                >>> # FastTreeValue 1 will be FastTreeValue({'x': [1, 2], 'y': [5, 6]})
                >>> # FastTreeValue 2 will be FastTreeValue({'x': [2, 3], 'y': [7, 8]})
            """
            return rise_func(self, dict_, list_, tuple_, template)

        @_decorate_method
        def graph(self, root: Optional[str] = None, title: Optional[str] = None,
                  cfg: Optional[dict] = None,
                  dup_value: Union[bool, Callable, type, Tuple[Type, ...]] = False,
                  repr_gen: Optional[Callable] = None,
                  node_cfg_gen: Optional[Callable] = None,
                  edge_cfg_gen: Optional[Callable] = None) -> Digraph:
            """
            Overview:
                Draw graph of this tree value.

            Args:
                - root (:obj:`Optional[str]`): Root name of the graph, default is ``None``, \
                    this name will be automatically generated.
                - title (:obj:`Optional[str]`): Title of the graph, default is ``None``, \
                    this title will be automatically generated from ``root`` argument.
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
            root = root or ('<%s #%x>' % (type(self).__name__, id(self._detach())))
            title = title or ('Graph of tree %s.' % (root,))
            return graphics(
                (self, root), title=title, cfg=cfg, dup_value=dup_value,
                repr_gen=repr_gen, node_cfg_gen=node_cfg_gen, edge_cfg_gen=edge_cfg_gen,
            )

        @classmethod
        @_decorate_method
        def func(cls, mode: str = 'strict', inherit: bool = True,
                 missing: Union[Any, Callable] = MISSING_NOT_ALLOW, delayed: bool = False,
                 subside: Union[Mapping, bool, None] = None, rise: Union[Mapping, bool, None] = None):
            """
            Overview:
                Wrap a common function to tree-supported function based on this type.

            Arguments:
                - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
                - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
                - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
                    default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
                - delayed (:obj:`bool`): Enable delayed mode or not, the calculation will be delayed when enabled, \
                    default is ``False``, which means to all the calculation at once.
                - subside (:obj:`Union[Mapping, bool, None]`): Subside enabled to function's arguments or not, \
                    and subside configuration, default is `None` which means do not use subside. \
                    When subside is `True`, it will use all the default arguments in `subside` function.
                - rise (:obj:`Union[Mapping, bool, None]`): Rise enabled to function's return value or not, \
                    and rise configuration, default is `None` which means do not use rise. \
                    When rise is `True`, it will use all the default arguments in `rise` function. \
                    (Not recommend to use auto mode when your return structure is not so strict.)

            Returns:
                - decorator (:obj:`Callable`): Wrapper for tree-supported function.

            Example:
                >>> from treevalue import FastTreeValue
                >>>
                >>> @FastTreeValue.func()
                >>> def ssum(a, b):
                >>>     return a + b  # the a and b will be integers, not TreeValue
                >>>
                >>> t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
                >>> ssum(1, 2)    # 3
                >>> ssum(t1, t2)  # FastTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 9}})
            """
            return func_treelize(mode, cls, inherit, missing, delayed, subside, rise)

        @classmethod
        @_decorate_method
        def union(cls, *trees, return_type=None, **kwargs):
            """
            Overview:
                Union tree values together.

            Arguments:
                - trees (:obj:`_TreeValue`): Tree value objects.
                - mode (:obj:): Mode of the wrapping, default is `strict`.
                - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, default is `TreeValue`.
                - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
                - missing (:obj:): Missing value or lambda generator of when missing, default is `MISSING_NOT_ALLOW`, which \
                    means raise `KeyError` when missing detected.

            Returns:
                - result (:obj:`TreeValue`): Unionised tree value.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> tx = t.map(lambda v: v % 2 == 1)
                >>> FastTreeValue.union(t, tx)  # FastTreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})
            """
            return union(*trees, return_type=return_type or cls, **kwargs)

        @classmethod
        @_decorate_method
        def subside(cls, value, dict_: bool = True, list_: bool = True, tuple_: bool = True,
                    return_type: Optional[Type[_TreeValue]] = None, **kwargs):
            """
            Overview:
                Drift down the structures (list, tuple, dict) down to the tree's value.

            Arguments:
                - value (:obj:): Original value object, may be nested dict, list or tuple.
                - `dict_` (:obj:`bool`): Enable dict subside, default is `True`.
                - `list_` (:obj:`bool`): Enable list subside, default is `True`.
                - `tuple_` (:obj:`bool`): Enable list subside, default is `True`.
                - mode (:obj:): Mode of the wrapping, default is `strict`.
                - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, \
                    will be auto detected when there is exactly one tree value type in this original value, \
                    otherwise the default will be `TreeValue`.
                - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
                - missing (:obj:): Missing value or lambda generator of when missing, default is `MISSING_NOT_ALLOW`, which \
                    means raise `KeyError` when missing detected.

            Returns:
                - return (:obj:`_TreeValue`): Subsided tree value.

            Example:
                >>> data = {
                >>>     'a': TreeValue({'a': 1, 'b': 2}),
                >>>     'x': {
                >>>         'c': TreeValue({'a': 3, 'b': 4}),
                >>>         'd': [
                >>>             TreeValue({'a': 5, 'b': 6}),
                >>>             TreeValue({'a': 7, 'b': 8}),
                >>>         ]
                >>>     },
                >>>     'k': '233'
                >>> }
                >>>
                >>> tree = FastTreeValue.subside(data)
                >>> # tree should be --> FastTreeValue({
                >>> #    'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
                >>> #    'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
                >>> #}), all structures above the tree values are subsided to the bottom of the tree.
            """
            return subside_func(value, dict_, list_, tuple_,
                                return_type=return_type or cls, **kwargs)

        @classmethod
        @_decorate_method
        def graphics(cls, *trees, title: Optional[str] = None, cfg: Optional[dict] = None,
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
            return graphics(
                *trees, title=title, cfg=cfg, dup_value=dup_value,
                repr_gen=repr_gen, node_cfg_gen=node_cfg_gen, edge_cfg_gen=edge_cfg_gen,
            )

        @_decorate_treelize
        def __add__(self, other):
            """
            Overview:
                Add tree values together.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 + t2  # FastTreeValue({'a': 12, 'b': 24, 'x': {'c': 33, 'd': 44}})
            """
            return self + other

        @_decorate_treelize
        def __radd__(self, other):
            """
            Overview:
                Right version of `__add__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 1 + t1  # FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
            """
            return other + self

        @_decorate_and_replace
        def __iadd__(self, other):
            """
            Overview:
                Self version of `__add__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 += t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 12, 'b': 24, 'x': {'c': 33, 'd': 44}})
            """
            self += other
            return self

        @_decorate_treelize
        def __sub__(self, other):
            """
            Overview:
                Substract tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 - t2  # FastTreeValue({'a': -10, 'b': -20, 'x': {'c': -27, 'd': -36}})
            """
            return self - other

        @_decorate_treelize
        def __rsub__(self, other):
            """
            Overview:
                Right version of `__sub__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 1 - t1  # FastTreeValue({'a': 0, 'b': -1, 'x': {'c': -2, 'd': -3}})
            """
            return other - self

        @_decorate_and_replace
        def __isub__(self, other):
            """
            Overview:
                Self version of `__sub__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 -= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': -10, 'b': -20, 'x': {'c': -27, 'd': -36}})
            """
            self -= other
            return self

        @_decorate_treelize
        def __mul__(self, other):
            """
            Overview:
                Multiply tree values together.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 * t2  # FastTreeValue({'a': 11, 'b': 44, 'x': {'c': 90, 'd': 160}})
            """
            return self * other

        @_decorate_treelize
        def __rmul__(self, other):
            """
            Overview:
                Right version of `__mul__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 2 * t1  # FastTreeValue({'a': 2, 'b': 4, 'x': {'c': 6, 'd': 8}})
            """
            return other * self

        @_decorate_and_replace
        def __imul__(self, other):
            """
            Overview:
                Self version of `__mul__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 40}})
                >>> t1 *= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 11, 'b': 44, 'x': {'c': 90, 'd': 160}})
            """
            self *= other
            return self

        @_decorate_treelize
        def __matmul__(self, other):
            """
            Overview:
                Matrix tree values together, can be used in numpy or torch.
            """
            return self @ other

        @_decorate_treelize
        def __rmatmul__(self, other):
            """
            Overview:
                Right version of `__matmul__`.
            """
            return other @ self

        @_decorate_and_replace
        def __imatmul__(self, other):
            """
            Overview:
                Self version of `__matmul__`.
                Original id of self will be kept.
            """
            self @= other
            return self

        @_decorate_treelize
        def __truediv__(self, other):
            """
            Overview:
                True divide tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t1 / t2  # FastTreeValue({'a': 0.1, 'b': 0.08, 'x': {'c': 0.1, 'd': 0.1}})
            """
            return self / other

        @_decorate_treelize
        def __rtruediv__(self, other):
            """
            Overview:
                Right version of `__truediv__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 / t1  # FastTreeValue({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1.5}})
            """
            return other / self

        @_decorate_and_replace
        def __itruediv__(self, other):
            """
            Overview:
                Self version of `__truediv__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t1 /= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 0.1, 'b': 0.08, 'x': {'c': 0.1, 'd': 0.1}})
            """
            self /= other
            return self

        @_decorate_treelize
        def __floordiv__(self, other):
            """
            Overview:
                Floor divide tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t2 // t1  # FastTreeValue({'a': 10, 'b': 12, 'x': {'c': 10, 'd': 10}})
            """
            return self // other

        @_decorate_treelize
        def __rfloordiv__(self, other):
            """
            Overview:
                Right version of `__floordiv__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 // t1  # FastTreeValue({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1}})
            """
            return other // self

        @_decorate_and_replace
        def __ifloordiv__(self, other):
            """
            Overview:
                Self version of `__floordiv__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t2 //= t1
                >>> t2 # t2's id will not change, FastTreeValue({'a': 10, 'b': 12, 'x': {'c': 10, 'd': 10}})
            """
            self //= other
            return self

        @_decorate_treelize
        def __mod__(self, other):
            """
            Overview:
                Mod tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t2 % t1  # FastTreeValue({'a': 0, 'b': 1, 'x': {'c': 0, 'd': 0}})
            """
            return self % other

        @_decorate_treelize
        def __rmod__(self, other):
            """
            Overview:
                Right version of `__mod__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 % t1  # FastTreeValue({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 2}})
            """
            return other % self

        @_decorate_and_replace
        def __imod__(self, other):
            """
            Overview:
                Self version of `__mod__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 10, 'b': 25, 'x': {'c': 30, 'd': 40}})
                >>> t2 %= t1
                >>> t2 # t2's id will not change, FastTreeValue({'a': 0, 'b': 1, 'x': {'c': 0, 'd': 0}})
            """
            self %= other
            return self

        @_decorate_treelize
        def __pow__(self, power):
            """
            Overview:
                Mod tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 ** t2  # FastTreeValue({'a': 1, 'b': 8, 'x': {'c': 81, 'd': 1024}})
            """
            return self ** power

        @_decorate_treelize
        def __rpow__(self, other):
            """
            Overview:
                Right version of `__pow__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 2 ** t1  # FastTreeValue({'a': 2, 'b': 4, 'x': {'c': 8, 'd': 16}})
            """
            return other ** self

        @_decorate_and_replace
        def __ipow__(self, other):
            """
            Overview:
                Self version of `__pow__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 **= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 1, 'b': 8, 'x': {'c': 81, 'd': 1024}})
            """
            self **= other
            return self

        @_decorate_treelize
        def __and__(self, other):
            """
            Overview:
                Bitwise and tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 & t2  # FastTreeValue({'a': 0, 'b': 2, 'x': {'c': 0, 'd': 4}})
            """
            return self & other

        @_decorate_treelize
        def __rand__(self, other):
            """
            Overview:
                Right version of `__and__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 & t1  # FastTreeValue({'a': 1, 'b': 0, 'x': {'c': 1, 'd': 4}})
            """
            return other & self

        @_decorate_and_replace
        def __iand__(self, other):
            """
            Overview:
                Self version of `__and__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 &= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 0, 'b': 2, 'x': {'c': 0, 'd': 4}})
            """
            self &= other
            return self

        @_decorate_treelize
        def __or__(self, other):
            """
            Overview:
                Bitwise or tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 | t2  # FastTreeValue({'a': 3, 'b': 3, 'x': {'c': 7, 'd': 5}})
            """
            return self | other

        @_decorate_treelize
        def __ror__(self, other):
            """
            Overview:
                Right version of `__or__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 | t1  # FastTreeValue({'a': 5, 'b': 7, 'x': {'c': 7, 'd': 5}})
            """
            return other | self

        @_decorate_and_replace
        def __ior__(self, other):
            """
            Overview:
                Self version of `__or__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 |= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 3, 'b': 3, 'x': {'c': 7, 'd': 5}})
            """
            self |= other
            return self

        @_decorate_treelize
        def __xor__(self, other):
            """
            Overview:
                Bitwise or tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 ^ t2  # FastTreeValue({'a': 3, 'b': 1, 'x': {'c': 7, 'd': 1}})
            """
            return self ^ other

        @_decorate_treelize
        def __rxor__(self, other):
            """
            Overview:
                Right version of `__xor__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 ^ t1  # FastTreeValue({'a': 4, 'b': 7, 'x': {'c': 6, 'd': 1}})
            """
            return other ^ self

        @_decorate_and_replace
        def __ixor__(self, other):
            """
            Overview:
                Self version of `__xor__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 ^= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 3, 'b': 1, 'x': {'c': 7, 'd': 1}})
            """
            self ^= other
            return self

        @_decorate_treelize
        def __lshift__(self, other):
            """
            Overview:
                Left shift tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 << t2  # FastTreeValue({'a': 4, 'b': 16, 'x': {'c': 48, 'd': 128}})
            """
            return self << other

        @_decorate_treelize
        def __rlshift__(self, other):
            """
            Overview:
                Right version of `__lshift__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 3 << t1  # FastTreeValue({'a': 6, 'b': 12, 'x': {'c': 24, 'd': 48}})
            """
            return other << self

        @_decorate_and_replace
        def __ilshift__(self, other):
            """
            Overview:
                Self version of `__xor__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1 <<= t2
                >>> t1 # t1's id will not change, FastTreeValue({'a': 4, 'b': 16, 'x': {'c': 48, 'd': 128}})
            """
            self <<= other
            return self

        @_decorate_treelize
        def __rshift__(self, other):
            """
            Overview:
                Left shift tree values.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 20, 'b': 30, 'x': {'c': 40, 'd': 50}})
                >>> t2 >> t1  # FastTreeValue({'a': 10, 'b': 7, 'x': {'c': 5, 'd': 3}})
            """
            return self >> other

        @_decorate_treelize
        def __rrshift__(self, other):
            """
            Overview:
                Right version of `__rshift__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 64 >> t1  # FastTreeValue({'a': 32, 'b': 16, 'x': {'c': 8, 'd': 4}})
            """
            return other >> self

        @_decorate_and_replace
        def __irshift__(self, other):
            """
            Overview:
                Self version of `__xor__`.
                Original id of self will be kept.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t2 = FastTreeValue({'a': 20, 'b': 30, 'x': {'c': 40, 'd': 50}})
                >>> t2 >>= t1
                >>> t2 # t2's id will not change, FastTreeValue({'a': 10, 'b': 7, 'x': {'c': 5, 'd': 3}})
            """
            self >>= other
            return self

        @_decorate_treelize
        def __pos__(self):
            """
            Overview:
                Positive tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> +t1  # FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            """
            return +self

        @_decorate_treelize
        def __neg__(self):
            """
            Overview:
                Negative tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> -t1  # FastTreeValue({'a': -1, 'b': -2, 'x': {'c': -3, 'd': -4}})
            """
            return -self

        @_decorate_treelize
        def __invert__(self):
            """
            Overview:
                Bitwise invert tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': -2, 'x': {'c': 3, 'd': -4}})
                >>> ~t1  # FastTreeValue({'a': -2, 'b': 1, 'x': {'c': -4, 'd': 3}})
            """
            return ~self

        @method_treelize()
        def _getitem_extern(self, item):
            return self[item]

        def __getitem__(self, item):
            """
            Overview:
                Get item of tree values.

            Examples:
                >>> from treevalue import FastTreeValue
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> t1['a']  # key access
                [1, 2]
                >>> t1[0]  # value access
                <FastTreeValue 0x7fa9c8c36cf8>
                ├── 'a' --> 1
                ├── 'b' --> 2
                └── 'x' --> <FastTreeValue 0x7fa9c8c369e8>
                    ├── 'c' --> 3
                    └── 'd' --> 4
                >>> t1[-1]
                <FastTreeValue 0x7fa9c8a72dd8>
                ├── 'a' --> 2
                ├── 'b' --> 3
                └── 'x' --> <FastTreeValue 0x7fa9c8c36978>
                    ├── 'c' --> 4
                    └── 'd' --> 5
                >>> t1[::-1]
                <FastTreeValue 0x7fa9c8c36d30>
                ├── 'a' --> [2, 1]
                ├── 'b' --> [3, 2]
                └── 'x' --> <FastTreeValue 0x7fa9c8c36cf8>
                    ├── 'c' --> [4, 3]
                    └── 'd' --> [5, 4]
                >>> t1['x'][0]  # mixed access
                <FastTreeValue 0x7fa9c8a7b0b8>
                ├── 'c' --> 3
                └── 'd' --> 4

            .. note::
                If you need to get the string items from the node values, you can use double bracket. \
                For example

                >>> from treevalue import FastTreeValue, raw
                >>> tv4 = FastTreeValue({
                ...     'a': raw({'a': 1, 'y': 2}),
                ...     'c': {'x': raw({'a': 3, 'y': 4})},
                ... })
                >>> tv4['a']  # key access
                {'a': 1, 'y': 2}
                >>> tv4[['a']]  # value access
                <FastTreeValue 0x7fa9c8c36588>
                ├── 'a' --> 1
                └── 'c' --> <FastTreeValue 0x7fa9c8a7b0b8>
                    └── 'x' --> 3
            """
            return TreeValue.__getitem__(self, item)

        @method_treelize()
        def _setitem_extern(self, key, value):
            self[key] = value

        def __setitem__(self, key, value):
            """
            Overview:
                Set item of tree values.

            Examples:
                >>> from treevalue import FastTreeValue
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> t1[0] = -2
                >>> t1
                <FastTreeValue 0x7fa9c8c36518>
                ├── 'a' --> [-2, 2]
                ├── 'b' --> [-2, 3]
                └── 'x' --> <FastTreeValue 0x7fa9c8a72dd8>
                    ├── 'c' --> [-2, 4]
                    └── 'd' --> [-2, 5]
                >>> t1[0] = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1
                <FastTreeValue 0x7fa9c8c36518>
                ├── 'a' --> [2, 2]
                ├── 'b' --> [3, 3]
                └── 'x' --> <FastTreeValue 0x7fa9c8a72dd8>
                    ├── 'c' --> [4, 4]
                    └── 'd' --> [5, 5]
                >>> t1['b'] = [22, 33]
                >>> t1
                <FastTreeValue 0x7fa9c8c36518>
                ├── 'a' --> [2, 2]
                ├── 'b' --> [22, 33]
                └── 'x' --> <FastTreeValue 0x7fa9c8a72dd8>
                    ├── 'c' --> [4, 4]
                    └── 'd' --> [5, 5]

            .. note::
                If you need to set the string items from the node values, you can use double bracket. \
                For example

                >>> from treevalue import FastTreeValue, raw
                >>> tv4 = FastTreeValue({
                ...     'a': raw({'a': 1, 'y': 2}),
                ...     'c': {'x': raw({'a': 3, 'y': 4})},
                ... })
                >>> tv4['a'] = {'a': 11, 'y': 22}  # key access
                >>> tv4
                <FastTreeValue 0x7fa9c8c36588>
                ├── 'a' --> {'a': 11, 'y': 22}
                └── 'c' --> <FastTreeValue 0x7fa9c8c369e8>
                    └── 'x' --> {'a': 3, 'y': 4}
                >>> tv4[['a']] = -2  # value access
                >>> tv4
                <FastTreeValue 0x7fa9c8c36588>
                ├── 'a' --> {'a': -2, 'y': 22}
                └── 'c' --> <FastTreeValue 0x7fa9c8c369e8>
                    └── 'x' --> {'a': -2, 'y': 4}
            """
            TreeValue.__setitem__(self, key, value)

        @method_treelize()
        def _delitem_extern(self, key):
            del self[key]

        def __delitem__(self, key):
            """
            Overview:
                Delete item of tree values.

            Examples:
                >>> from treevalue import FastTreeValue, raw
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> del t1[0]
                >>> t1
                <FastTreeValue 0x7fa9c8c366a0>
                ├── 'a' --> [2]
                ├── 'b' --> [3]
                └── 'x' --> <FastTreeValue 0x7fa9c8a7b0b8>
                    ├── 'c' --> [4]
                    └── 'd' --> [5]
                >>> del t1['b']
                >>> t1
                <FastTreeValue 0x7fa9c8c366a0>
                ├── 'a' --> [2]
                └── 'x' --> <FastTreeValue 0x7fa9c8a7b0b8>
                    ├── 'c' --> [4]
                    └── 'd' --> [5]

            .. note::
                If you need to delete the string items from the node values, you can use double bracket. \
                For example

                >>> from treevalue import FastTreeValue, raw
                >>> tv4 = FastTreeValue({
                ...     'a': raw({'a': 1, 'y': 2}),
                ...     'c': {'x': raw({'a': 3, 'y': 4})},
                ...     'g': {'x': raw({'a': 31, 'y': 42})},
                ... })
                >>> del tv4['g']  # key delete
                >>> tv4
                <FastTreeValue 0x7fa9c8c36978>
                ├── 'a' --> {'a': 1, 'y': 2}
                └── 'c' --> <FastTreeValue 0x7fa9c8c36d30>
                    └── 'x' --> {'a': 3, 'y': 4}
                >>> del tv4[['a']]  # value delete
                >>> tv4
                <FastTreeValue 0x7fa9c8c36978>
                ├── 'a' --> {'y': 2}
                └── 'c' --> <FastTreeValue 0x7fa9c8c36d30>
                    └── 'x' --> {'y': 4}
            """
            return TreeValue.__delitem__(self, key)

        @_decorate_treelize
        def __call__(self, *args, **kwargs):
            """
            Overview:
                Call of tree values.

            Example:
                >>> class Container:
                >>>     def __init__(self, value):
                >>>         self.__value = value
                >>>
                >>>     def append(self, v):
                >>>         return self.__value + v
                >>>
                >>> t = FastTreeValue({'a': Container(1), 'b': Container(2)})
                >>> t.append(2)  # FastTreeValue({'a': 3, 'b': 4})
                >>> t.append(FastTreeValue({'a': 10, 'b': 20}))  # FastTreeValue({'a': 11, 'b': 22})
            """
            return self(*args, **kwargs)

    return _GeneralTreeValue
