from enum import IntEnum
from functools import wraps
from typing import Type, TypeVar, Optional

from .inner import _InnerProcessor
from .left import _LeftProcessor
from .outer import _OuterProcessor
from .strict import _StrictProcessor
from ..tree.tree import TreeValue
from ...utils import int_enum_loads


@int_enum_loads(name_preprocess=str.upper)
class TreeMode(IntEnum):
    STRICT = 1
    LEFT = 2
    INNER = 3
    OUTER = 4


_MODE_PROCESSORS = {
    TreeMode.STRICT: _StrictProcessor(),
    TreeMode.LEFT: _LeftProcessor(),
    TreeMode.INNER: _InnerProcessor(),
    TreeMode.OUTER: _OuterProcessor(),
}


def _any_getattr(value):
    class _AnyClass:
        def __getattr__(self, item):
            return value

    return _AnyClass()


_ClassType = TypeVar("_ClassType", bound=TreeValue)


def func_treelize(mode='strict', return_type: Optional[Type[_ClassType]] = TreeValue,
                  allow_inherit: bool = False, allow_missing: bool = False,
                  missing_value=None, missing_func=None):
    mode = TreeMode.loads(mode)
    missing_func = missing_func or (lambda: missing_value)
    _MODE_PROCESSORS[mode].check_arguments(mode, return_type, allow_inherit,
                                           allow_missing, missing_value, missing_func)

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
        def _new_func(*args, **kwargs) -> Optional[_ClassType]:
            if all([not isinstance(item, TreeValue) for item in args]) \
                    and all([not isinstance(value, TreeValue) for value in kwargs.values()]):
                return func(*args, **kwargs)

            pargs = [_value_wrap(item, index) for index, item in enumerate(args)]
            pkwargs = {key: _value_wrap(value, key) for key, value in kwargs.items()}

            _data = {
                key: _new_func(
                    *(item(key) for item in pargs),
                    **{key_: value(key) for key_, value in pkwargs.items()}
                ) for key in sorted(_MODE_PROCESSORS[mode].get_key_set(*args, **kwargs))
            }
            return return_type(_data) if return_type is not None else None

        return _new_func

    return _decorator
