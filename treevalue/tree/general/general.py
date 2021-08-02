from functools import lru_cache
from typing import List, Mapping, Optional, Any, Type, TypeVar, Union, Callable

from ..func import method_treelize
from ..tree import TreeValue, jsonify, view, clone, typetrans, mapping, mask, filter_, reduce_, union, subside, rise, \
    NO_RISE_TEMPLATE

_BASE_GENERATION_CONFIG = {}


def general_tree_value(base: Optional[Mapping[str, Any]] = None,
                       methods: Optional[Mapping[str, Optional[Mapping[str, Any]]]] = None):
    """
    Overview:
        Get general tree value class.

    Arguments:
        - base (:obj:`Optional[Mapping[str, Any]]`): Base configuration of `func_treelize`.
        - methods (:obj:`Optional[Mapping[str, Optional[Mapping[str, Any]]]]`): Method configurations of `func_treelize`.

    Returns:
        - clazz (:obj:`Type[TreeValue]`): General tree value class.
    """
    base = base or {}
    methods = methods or {}

    @lru_cache()
    def _decorator_config(name):
        _config = _BASE_GENERATION_CONFIG.copy()
        _config.update(base)
        _config.update(methods.get(name, None) or {})
        return _config

    def _decorate(func):
        return method_treelize(**_decorator_config(func.__name__))(func)

    _TreeValue = TypeVar("_TreeValue", bound=TreeValue)

    # noinspection PyUnresolvedReferences
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

        def view(self, path: List[str]):
            """
            Overview:
                Create a `TreeValue` object which is a view of the current tree.

            Arguments:
                - path (:obj:`List[str]`): Path of the view.

            Returns:
                - tree (:obj:`_TreeValue`): Viewed tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.view(['x'])  # FastTreeValue({'c': 3, 'd': 4}), it is a view not the real node
            """
            return view(self, path)

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

        def map(self, mapper):
            """
            Overview:
                Do mapping on every value in this tree.

            Arguments:
                - func (:obj:): Function for mapping

            Returns:
                - tree (:obj:`_TreeValue`): Mapped tree value object.

            Example:
                >>> t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t.map(lambda x: x + 2)  # FastTreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
                >>> t.map(lambda: 1)        # FastTreeValue({'a': 1, 'b': 1, 'x': {'c': 1, 'd': 1}})
                >>> t.map(lambda x, p: p)   # FastTreeValue({'a': ('a',), 'b': ('b',), 'x': {'c': ('x', 'c'), 'd': ('x', 'd')}})
            """
            return mapping(self, mapper)

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

        def rise(self, dict_: bool = True, list_: bool = True, tuple_: bool = True,
                 template=NO_RISE_TEMPLATE):
            """
            Overview:
                Make the structure (dict, list, tuple) in value rise up to the top, above the tree value.

            Arguments:
                - `dict_` (:obj:`bool`): Enable dict rise, default is `True`.
                - `list_` (:obj:`bool`): Enable list rise, default is `True`.
                - `tuple_` (:obj:`bool`): Enable list rise, default is `True`.
                - template (:obj:): Rising template, default is `NO_RISE_TEMPLATE`, which means auto detect.

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
            return rise(self, dict_, list_, tuple_)

        @classmethod
        def union(cls, *trees, return_type=None, **kwargs):
            """
            Overview:
                Union tree values together.

            Arguments:
                - trees (:obj:`_TreeValue`): Tree value objects.
                - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
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
                - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
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
            return subside(value, dict_, list_, tuple_,
                           return_type=return_type or cls, **kwargs)

        @_decorate
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

        @_decorate
        def __radd__(self, other):
            """
            Overview:
                Right version of `__add__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 1 + t1  # FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
            """
            return other + self

        @_decorate
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

        @_decorate
        def __rsub__(self, other):
            """
            Overview:
                Right version of `__sub__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 1 - t1  # FastTreeValue({'a': 0, 'b': -1, 'x': {'c': -2, 'd': -3}})
            """
            return other - self

        @_decorate
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

        @_decorate
        def __rmul__(self, other):
            """
            Overview:
                Right version of `__mul__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 2 * t1  # FastTreeValue({'a': 2, 'b': 4, 'x': {'c': 6, 'd': 8}})
            """
            return other * self

        @_decorate
        def __matmul__(self, other):
            """
            Overview:
                Matrix tree values together, can be used in numpy or torch.
            """
            return self @ other

        @_decorate
        def __rmatmul__(self, other):
            """
            Overview:
                Right version of `__matmul__`.
            """
            return other @ self

        @_decorate
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

        @_decorate
        def __rtruediv__(self, other):
            """
            Overview:
                Right version of `__truediv__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 / t1  # FastTreeValue({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1.5}})
            """
            return other / self

        @_decorate
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

        @_decorate
        def __rfloordiv__(self, other):
            """
            Overview:
                Right version of `__floordiv__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 // t1  # FastTreeValue({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1}})
            """
            return other // self

        @_decorate
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

        @_decorate
        def __rmod__(self, other):
            """
            Overview:
                Right version of `__mod__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 6 % t1  # FastTreeValue({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 2}})
            """
            return other % self

        @_decorate
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

        @_decorate
        def __rpow__(self, other):
            """
            Overview:
                Right version of `__pow__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 2 ** t1  # FastTreeValue({'a': 2, 'b': 4, 'x': {'c': 8, 'd': 16}})
            """
            return other ** self

        @_decorate
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

        @_decorate
        def __rand__(self, other):
            """
            Overview:
                Right version of `__and__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 & t1  # FastTreeValue({'a': 1, 'b': 0, 'x': {'c': 1, 'd': 4}})
            """
            return other & self

        @_decorate
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

        @_decorate
        def __ror__(self, other):
            """
            Overview:
                Right version of `__or__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 | t1  # FastTreeValue({'a': 5, 'b': 7, 'x': {'c': 7, 'd': 5}})
            """
            return other | self

        @_decorate
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

        @_decorate
        def __rxor__(self, other):
            """
            Overview:
                Right version of `__xor__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 5 ^ t1  # FastTreeValue({'a': 4, 'b': 7, 'x': {'c': 6, 'd': 1}})
            """
            return other ^ self

        @_decorate
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

        @_decorate
        def __rlshift__(self, other):
            """
            Overview:
                Right version of `__lshift__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 3 << t1  # FastTreeValue({'a': 6, 'b': 12, 'x': {'c': 24, 'd': 48}})
            """
            return other << self

        @_decorate
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

        @_decorate
        def __rrshift__(self, other):
            """
            Overview:
                Right version of `__rshift__`.

            Example:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> 64 >> t1  # FastTreeValue({'a': 32, 'b': 16, 'x': {'c': 8, 'd': 4}})
            """
            return other >> self

        @_decorate
        def __pos__(self):
            """
            Overview:
                Positive tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> +t1  # FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            """
            return +self

        @_decorate
        def __neg__(self):
            """
            Overview:
                Negative tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> -t1  # FastTreeValue({'a': -1, 'b': -2, 'x': {'c': -3, 'd': -4}})
            """
            return -self

        @_decorate
        def __invert__(self):
            """
            Overview:
                Bitwise invert tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': 1, 'b': -2, 'x': {'c': 3, 'd': -4}})
                >>> ~t1  # FastTreeValue({'a': -2, 'b': 1, 'x': {'c': -4, 'd': 3}})
            """
            return ~self

        @_decorate
        def __getitem__(self, item):
            """
            Overview:
                Get item of tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> t1[0]     # FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
                >>> t1[-1]    # FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> t1[::-1]  # FastTreeValue({'a': [2, 1], 'b': [3, 2], 'x': {'c': [4, 3], 'd': [5, 4]}})
            """
            return self[item]

        @_decorate
        def __setitem__(self, key, value):
            """
            Overview:
                Set item of tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> t1[0] = -2  # FastTreeValue({'a': [-2, 2], 'b': [-2, 3], 'x': {'c': [-2, 4], 'd': [-2, 5]}})
                >>> t1[0] = FastTreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
                >>> # FastTreeValue({'a': [2, 2], 'b': [3, 3], 'x': {'c': [4, 4], 'd': [5, 5]}})
            """
            self[key] = value

        @_decorate
        def __delitem__(self, key):
            """
            Overview:
                Delete item of tree values.

            Examples:
                >>> t1 = FastTreeValue({'a': [1, 2], 'b': [2, 3], 'x': {'c': [3, 4], 'd': [4, 5]}})
                >>> del t1[0]  # FastTreeValue({'a': [2], 'b': [3], 'x': {'c': [4], 'd': [5]}})
            """
            del self[key]

        @_decorate
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
