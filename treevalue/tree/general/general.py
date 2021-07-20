from functools import lru_cache
from typing import List, Mapping, Optional, Any

from ..func import method_treelize
from ..tree import TreeValue, jsonify, view, clone


@lru_cache()
def _get_method_by_name(name):
    def _func(self, *args, **kwargs):
        return getattr(self, name)(*args, **kwargs)

    return _func


BASE_CONFIG = dict(inherit=True)


def general_tree_value(base: Optional[Mapping[str, Any]] = None,
                       methods: Optional[Mapping[str, Optional[Mapping[str, Any]]]] = None):
    if base is None:
        base = BASE_CONFIG
    base = base or {}
    methods = methods or {}

    @lru_cache()
    def _decorator_config(name):
        _config = base.copy()
        _config.update(methods.get(name, {}))
        return _config

    def _decorate(func):
        print(func.__name__)
        return method_treelize(**_decorator_config(func.__name__))(func)

    class _GeneralTreeValue(TreeValue):
        @method_treelize(inherit=True)
        def _attr_extern(self, key):
            return getattr(self, key)

        def json(self):
            return jsonify(self)

        def view(self, path: List[str]):
            return view(self, path)

        def clone(self):
            return clone(self)

        @_decorate
        def __add__(self, other):
            return _get_method_by_name('__add__')(self, other)

        @_decorate
        def __radd__(self, other):
            return _get_method_by_name('__radd__')(self, other)

        @_decorate
        def __sub__(self, other):
            return _get_method_by_name('__sub__')(self, other)

        @_decorate
        def __rsub__(self, other):
            return _get_method_by_name('__rsub__')(self, other)

        @_decorate
        def __mul__(self, other):
            return _get_method_by_name('__mul__')(self, other)

        @_decorate
        def __rmul__(self, other):
            return _get_method_by_name('__rmul__')(self, other)

        @_decorate
        def __matmul__(self, other):
            return _get_method_by_name('__matmul__')(self, other)

        @_decorate
        def __rmatmul__(self, other):
            return _get_method_by_name('__rmatmul__')(self, other)

        @_decorate
        def __truediv__(self, other):
            return _get_method_by_name('__truediv__')(self, other)

        @_decorate
        def __rtruediv__(self, other):
            return _get_method_by_name('__rtruediv__')(self, other)

        @_decorate
        def __floordiv__(self, other):
            return _get_method_by_name('__floordiv__')(self, other)

        @_decorate
        def __rfloordiv__(self, other):
            return _get_method_by_name('__rfloordiv__')(self, other)

        @_decorate
        def __mod__(self, other):
            return _get_method_by_name('__mod__')(self, other)

        @_decorate
        def __rmod__(self, other):
            return _get_method_by_name('__rmod__')(self, other)

        @_decorate
        def __pow__(self, power, modulo=None):
            return _get_method_by_name('__pow__')(self, power, modulo)

        @_decorate
        def __rpow__(self, other):
            return _get_method_by_name('__rpow__')(self, other)

        @_decorate
        def __and__(self, other):
            return _get_method_by_name('__and__')(self, other)

        @_decorate
        def __rand__(self, other):
            return _get_method_by_name('__rand__')(self, other)

        @_decorate
        def __or__(self, other):
            return _get_method_by_name('__or__')(self, other)

        @_decorate
        def __ror__(self, other):
            return _get_method_by_name('__ror__')(self, other)

        @_decorate
        def __xor__(self, other):
            return _get_method_by_name('__xor__')(self, other)

        @_decorate
        def __rxor__(self, other):
            return _get_method_by_name('__rxor__')(self, other)

        @_decorate
        def __lshift__(self, other):
            return _get_method_by_name('__lshift__')(self, other)

        @_decorate
        def __rlshift__(self, other):
            return _get_method_by_name('__rlshift__')(self, other)

        @_decorate
        def __rshift__(self, other):
            return _get_method_by_name('__rshift__')(self, other)

        @_decorate
        def __rrshift__(self, other):
            return _get_method_by_name('__rrshift__')(self, other)

        @_decorate
        def __pos__(self):
            return _get_method_by_name('__pos__')(self)

        @_decorate
        def __neg__(self):
            return _get_method_by_name('__neg__')(self)

        @_decorate
        def __invert__(self):
            return _get_method_by_name('__invert__')(self)

        @_decorate
        def __getitem__(self, item):
            return _get_method_by_name('__getitem__')(self, item)

        @_decorate
        def __setitem__(self, key, value):
            return _get_method_by_name('__setitem__')(self, key, value)

        @_decorate
        def __delitem__(self, key):
            return _get_method_by_name('__delitem__')(self, key)

        @_decorate
        def __call__(self, *args, **kwargs):
            return _get_method_by_name('__call__')(self, *args, **kwargs)

    return _GeneralTreeValue