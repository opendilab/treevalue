from enum import IntEnum
from functools import wraps

from .inner import get_key_set as get_inner_key_set
from .left import get_key_set as get_left_key_set
from .outer import get_key_set as get_outer_key_set
from .strict import get_key_set as get_strict_key_set
from ..tree.tree import TreeValue
from ...utils import int_enum_loads


@int_enum_loads(name_preprocess=str.upper)
class TreeMode(IntEnum):
    STRICT = 1
    LEFT = 2
    INNER = 3
    OUTER = 4


_KEY_ITERATORS = {
    TreeMode.STRICT: get_strict_key_set,
    TreeMode.LEFT: get_left_key_set,
    TreeMode.INNER: get_inner_key_set,
    TreeMode.OUTER: get_outer_key_set,
}


def _any_getattr(value):
    class _AnyClass:
        def __getattr__(self, item):
            return value

    return _AnyClass()


def func_treelize(mode='strict', allow_inherit: bool = False,
                  allow_missing: bool = False, missing_value=None, missing_func=None):
    mode = TreeMode.loads(mode)
    missing_func = missing_func or (lambda: missing_value)

    def _value_wrap(item, index):
        if isinstance(item, TreeValue):
            def _get_from_key(key):
                if key in item:
                    return item.__getattr__(key)
                elif allow_missing:
                    return missing_func()
                else:
                    raise KeyError("Missing is off, key {key} not found in {item}.".format(
                        key=repr(key), item=repr(item),
                    ))

            return _get_from_key
        elif allow_inherit:
            return _any_getattr(item).__getattr__
        else:
            raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                type=repr(type(item).__name__), index=repr(index),
            ))

    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            if all([not isinstance(item, TreeValue) for item in args]) \
                    and all([not isinstance(value, TreeValue) for value in kwargs.values()]):
                return func(*args, **kwargs)

            pargs = [_value_wrap(item, index) for index, item in enumerate(args)]
            pkwargs = {key: _value_wrap(value, key) for key, value in kwargs.items()}

            return TreeValue({
                key: _new_func(
                    *(item(key) for item in pargs),
                    **{key_: value(key) for key_, value in pkwargs.items()}
                ) for key in sorted(_KEY_ITERATORS[mode](*args, **kwargs))
            })

        return _new_func

    return _decorator
