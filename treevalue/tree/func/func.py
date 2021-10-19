from enum import IntEnum, unique
from functools import wraps, partial
from itertools import chain
from typing import Type, TypeVar, Optional, Mapping, Union, Callable, Any, Tuple

import enum_tools

from .inner import _InnerProcessor
from .left import _LeftProcessor
from .outer import _OuterProcessor
from .strict import _StrictProcessor
from ..common import raw
from ..tree import TreeValue
from ..tree import rise as rise_func
from ..tree import subside as subside_func
from ...utils import int_enum_loads, SingletonMark


@enum_tools.documentation.document_enum
@int_enum_loads(name_preprocess=str.upper)
@unique
class TreeMode(IntEnum):
    """
    Overview:
        Four mode of the tree calculation
    """
    STRICT = 1  # doc: Strict mode, which means the keys should be one to one in every trees.
    LEFT = 2  # doc: Left mode, the keys of the result is relied on the left value.
    INNER = 3  # doc: Inner mode, the keys of the result is relied on the intersection of the trees' key set.
    OUTER = 4  # doc: Outer mode, the keys of the result is relied on the union of the trees' key set.


_MODE_PROCESSORS = {
    TreeMode.STRICT: _StrictProcessor(),
    TreeMode.LEFT: _LeftProcessor(),
    TreeMode.INNER: _InnerProcessor(),
    TreeMode.OUTER: _OuterProcessor(),
}


def _get_any_value(item, value):
    return value


def _any_getattr(value):
    return partial(_get_any_value, value=value)


TreeClassType_ = TypeVar("TreeClassType_", bound=TreeValue)

#: Default value of the ``missing`` arguments of ``func_treelize``, ``method_treelize`` \
#: and ``classmethod_treelize``, which means missing is not allowed \
#: (raise ``KeyError`` when missing is detected).
MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")


def func_treelize(mode: Union[str, TreeMode] = 'strict',
                  return_type: Union[None, Type[TreeClassType_], Callable] = TreeValue,
                  inherit: bool = True,
                  missing: Union[Any, Callable] = MISSING_NOT_ALLOW,
                  subside: Union[Mapping, bool, None] = None,
                  rise: Union[Mapping, bool, None] = None):
    """
    Overview:
        Wrap a common function to tree-supported function.

    Arguments:
        - mode (:obj:`Union[str, TreeMode]`): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
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
        >>> @func_treelize()
        >>> def ssum(a, b):
        >>>     return a + b  # the a and b will be integers, not TreeValue
        >>>
        >>> t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        >>> ssum(1, 2)    # 3
        >>> ssum(t1, t2)  # TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 9}})
    """
    mode = TreeMode.loads(mode)
    processor = _MODE_PROCESSORS[mode]
    if missing is MISSING_NOT_ALLOW:
        allow_missing = False
        missing_func = None
    else:
        allow_missing = True
        missing_func = missing if hasattr(missing, '__call__') else (lambda: missing)

    if subside is not None and not isinstance(subside, dict):
        subside = {} if subside else None
    if rise is not None and not isinstance(rise, dict):
        rise = {} if rise else None

    processor.check_arguments(mode, return_type, inherit,
                              allow_missing, missing_func, subside, rise)

    def _get_from_key(key, item):
        if key in item:
            return item.__getattr__(key)
        elif allow_missing:
            return missing_func()
        else:
            raise KeyError("Missing is off, key {key} not found in {item}.".format(
                key=repr(key), item=repr(item),
            ))

    def _value_wrap(item, index):
        if isinstance(item, TreeValue):
            return partial(_get_from_key, item=item)
        elif inherit:
            return _any_getattr(item)
        else:
            raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                type=repr(type(item).__name__), index=repr(index),
            ))

    def _decorator(func):
        _get_key_set = processor.get_key_set

        def _recursion(*args, **kwargs) -> Tuple[TreeClassType_, bool]:
            is_const = True
            for v in chain(args, kwargs.values()):
                if isinstance(v, TreeValue):
                    is_const = False
                    break

            if is_const:
                return func(*args, **kwargs), True
            else:
                pargs = [_value_wrap(item, index) for index, item in enumerate(args)]
                pkwargs = {key: _value_wrap(value, key) for key, value in kwargs.items()}

                _data = {
                    key: raw(_recursion(
                        *(item(key) for item in pargs),
                        **{key_: value(key) for key_, value in pkwargs.items()}
                    )[0]) for key in _get_key_set(*args, **kwargs)
                }
                return TreeValue(_data), False

        @wraps(func)
        def _new_func(*args, **kwargs):
            if subside is not None:
                args = [subside_func(item, **subside) for item in args]
                kwargs = {key: subside_func(value, **subside) for key, value in kwargs.items()}

            _result, _is_const = _recursion(*args, **kwargs)
            if return_type is not None:
                if isinstance(return_type, type) and issubclass(return_type, TreeValue):
                    rt = return_type
                else:
                    rt = return_type(args[0])

                if not _is_const:
                    _result = rt(_result)
                if rise is not None:
                    _result = rise_func(_result, **rise)

                return _result
            else:
                return None

        return _new_func

    return _decorator


#: Default value of the ``return_type`` arguments \
#: of ``method_treelize`` and ``classmethod_treelize``, \
#: which means return type will be auto configured to
#: the current class.
AUTO_DETECT_RETURN_TYPE = SingletonMark("auto_detect_return_type")


def method_treelize(mode: Union[str, TreeMode] = 'strict',
                    return_type: Optional[Type[TreeClassType_]] = AUTO_DETECT_RETURN_TYPE, inherit: bool = True,
                    missing: Union[Any, Callable] = MISSING_NOT_ALLOW,
                    subside: Union[Mapping, bool, None] = None,
                    rise: Union[Mapping, bool, None] = None, self_copy: bool = False):
    """
    Overview:
        Wrap a common instance method to tree-supported method.

    Attention:
        - This decorator can only used to instance method, usage with class method may cause unconditional fatal.
        - When decorated instance method is called, the `self` argument will be no longer the class instance, \
            but the single element of the tree instead.

    Arguments:
        - mode (:obj:`Union[str, TreeMode]`): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, \
            default is `AUTO_DETECT_RETURN_VALUE`, which means automatically use the decorated method's class.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
        - subside (:obj:`Union[Mapping, bool, None]`): Subside enabled to function's arguments or not, \
            and subside configuration, default is `None` which means do not use subside. \
            When subside is `True`, it will use all the default arguments in `subside` function.
        - rise (:obj:`Union[Mapping, bool, None]`): Rise enabled to function's return value or not, \
            and rise configuration, default is `None` which means do not use rise. \
            When rise is `True`, it will use all the default arguments in `rise` function. \
            (Not recommend to use auto mode when your return structure is not so strict.)
        - self_copy (:obj:`bool`): Self copy mode, if enabled, the result data will be copied to \
            ``self`` argument and ``self`` will be returned as result. Default is ``False``, \
            which means do not do self copy.

    Returns:
        - decorator (:obj:`Callable`): Wrapper for tree-supported method.

    Example:
        >>> class MyTreeValue(TreeValue):
        >>>     @method_treelize()
        >>>     def append(self, *args):
        >>>         return sum([self, *args])  # the self will be the integers, not MyTreeValue
        >>>
        >>> t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> t2 = MyTreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        >>> t1.append(2)   # MyTreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
        >>> t1.append(t2)  # MyTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 9}})
    """

    def _decorator(method):
        if return_type is AUTO_DETECT_RETURN_TYPE:
            def _get_self_class(self):
                return self.__class__
        else:
            def _get_self_class(self):
                return return_type

        _treelized = func_treelize(mode, _get_self_class, inherit, missing, subside, rise)(method)

        @wraps(method)
        def _new_method(self, *args, **kwargs):
            _result = _treelized(self, *args, **kwargs)
            if self_copy:
                self._detach().copy_from(_result._detach())
                return self
            else:
                return _result

        return _new_method

    return _decorator


def classmethod_treelize(mode: Union[str, TreeMode] = 'strict',
                         return_type: Optional[Type[TreeClassType_]] = AUTO_DETECT_RETURN_TYPE, inherit: bool = True,
                         missing: Union[Any, Callable] = MISSING_NOT_ALLOW,
                         subside: Union[Mapping, bool, None] = None,
                         rise: Union[Mapping, bool, None] = None):
    """
    Overview:
        Wrap a common class method to tree-supported method.

    Attention:
        - This decorator can only used to class method, usage with instance method may cause unconditional fatal.
        - When decorated instance method is called, the `cls` argument will still be the calling class.

    Arguments:
        - mode (:obj:`Union[str, TreeMode]`): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, \
            default is `AUTO_DETECT_RETURN_VALUE`, which means automatically use the decorated method's class.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
        - subside (:obj:`Union[Mapping, bool, None]`): Subside enabled to function's arguments or not, \
            and subside configuration, default is `None` which means do not use subside. \
            When subside is `True`, it will use all the default arguments in `subside` function.
        - rise (:obj:`Union[Mapping, bool, None]`): Rise enabled to function's return value or not, \
            and rise configuration, default is `None` which means do not use rise. \
            When rise is `True`, it will use all the default arguments in `rise` function. \
            (Not recommend to use auto mode when your return structure is not so strict.)

    Returns:
        - decorator (:obj:`Callable`): Wrapper for tree-supported class method.

    Example:
        >>> class TestUtils:
        >>>     @classmethod
        >>>     @classmethod_treelize(return_type=TreeValue)
        >>>     def add(cls, a, b):
        >>>         return cls, a + b
        >>>
        >>> TestUtils.add(
        >>>     TreeValue({'a': 1, 'b': 2}),
        >>>     TreeValue({'a': 11, 'b': 23}),
        >>> )  # TreeValue({'a': (TestUtils, 12), 'b': (TestUtils, 25)})
    """

    if return_type is AUTO_DETECT_RETURN_TYPE:
        def _get_cls_class(cls):
            return cls
    else:
        def _get_cls_class(cls):
            return return_type

    return func_treelize(mode, _get_cls_class, inherit, missing, subside, rise)
