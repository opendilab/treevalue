from enum import IntEnum, unique
from functools import wraps, partial
from typing import Type, TypeVar, Optional, Mapping, Union, Callable, Any

import enum_tools

from .inner import _InnerProcessor
from .left import _LeftProcessor
from .outer import _OuterProcessor
from .strict import _StrictProcessor
from ..common import raw
from ..tree.tree import TreeValue, get_data_property
from ..tree.utils import rise as rise_func
from ..tree.utils import subside as subside_func
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


def _any_getattr(value):
    class _AnyClass:
        def __getattr__(self, item):
            return value

    return _AnyClass()


TreeClassType_ = TypeVar("TreeClassType_", bound=TreeValue)

#: Default value of the ``missing`` arguments of ``func_treelize``, ``method_treelize`` \
#: and ``classmethod_treelize``, which means missing is not allowed \
#: (raise ``KeyError`` when missing is detected).
MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")


def func_treelize(mode: Union[str, TreeMode] = 'strict',
                  return_type: Optional[Type[TreeClassType_]] = TreeValue, inherit: bool = True,
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

    _MODE_PROCESSORS[mode].check_arguments(mode, return_type, inherit,
                                           allow_missing, missing_func,
                                           subside, rise)

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
        elif inherit:
            return _any_getattr(item).__getattr__
        else:
            raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                type=repr(type(item).__name__), index=repr(index),
            ))

    def _decorator(func):
        def _recursion(*args, **kwargs) -> Optional[TreeClassType_]:
            if all([not isinstance(item, TreeValue) for item in args]) \
                    and all([not isinstance(value, TreeValue) for value in kwargs.values()]):
                return func(*args, **kwargs)

            pargs = [_value_wrap(item, index) for index, item in enumerate(args)]
            pkwargs = {key: _value_wrap(value, key) for key, value in kwargs.items()}

            _data = {
                key: raw(_recursion(
                    *(item(key) for item in pargs),
                    **{key_: value(key) for key_, value in pkwargs.items()}
                )) for key in sorted(_MODE_PROCESSORS[mode].get_key_set(*args, **kwargs))
            }
            return return_type(_data) if return_type is not None else None

        @wraps(func)
        def _new_func(*args, **kwargs):
            if subside is not None:
                args = [subside_func(item, **subside) for item in args]
                kwargs = {key: subside_func(value, **subside) for key, value in kwargs.items()}

            _result = _recursion(*args, **kwargs)
            if rise is not None:
                _result = rise_func(_result, **rise)

            return _result

        return _new_func

    return _decorator


_CONFIGS_TAG = '__configs__'


def _tree_check(clazz, allow_none=False):
    if clazz is None:
        if not allow_none:
            raise TypeError("Tree value class is not allowed to be none, but None found.")
        else:
            return

    if not isinstance(clazz, type):
        raise TypeError("Tree value class should be a type, but {type} found.".format(
            type=repr(type(clazz).__name__)
        ))
    elif not issubclass(clazz, TreeValue):
        raise TypeError("Tree value class should be subclass of TreeValue, but {type} found.".format(
            type=repr(clazz.__name__)
        ))


def _class_config(return_type: Optional[Type[TreeClassType_]] = None,
                  allow_none_return_type: bool = True,
                  clazz_must_be_tree_value: bool = True):
    _tree_check(return_type, allow_none=allow_none_return_type)

    def _decorator(clazz: type) -> type:
        if clazz_must_be_tree_value:
            _tree_check(clazz, allow_none=False)

        config = _get_configs(clazz)
        config.update(dict(
            return_type=return_type,
        ))
        setattr(clazz, _CONFIGS_TAG, config)
        return clazz

    return _decorator


def tree_class(return_type: Optional[Type[TreeClassType_]] = None):
    """
    Overview:
        Wrap tree configs for ``TreeValue`` class.

    Arguments:
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Default return type of current class, \
            default is ``None`` which means use the class itself.

    Returns:
        - decorator (:obj:`Callable`): A class decorator.
    """
    return _class_config(
        return_type, True, True,
    )


def _get_configs(clazz: type):
    return dict(getattr(clazz, _CONFIGS_TAG, None) or {})


#: Default value of the ``return_type`` arguments \
#: of ``method_treelize`` and ``classmethod_treelize``, \
#: which means return type will be auto configured to
#: the current class.
AUTO_DETECT_RETURN_TYPE = SingletonMark("auto_detect_return_type")


def _auto_detect_type(clazz: type):
    return _get_configs(clazz).get('return_type', None) or clazz


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
        @wraps(method)
        def _new_method(self, *args, **kwargs):
            rt = _auto_detect_type(self.__class__) if return_type is AUTO_DETECT_RETURN_TYPE else return_type
            _result = func_treelize(mode, rt, inherit, missing, subside, rise)(method)(self, *args, **kwargs)

            if self_copy:
                get_data_property(self).copy_from(get_data_property(_result))
                return self
            else:
                return _result

        return _new_method

    return _decorator


def utils_class(return_type: Type[TreeClassType_]):
    """
    Overview:
        Wrap tree configs for utils class.

    Arguments:
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Default return type of current class.

    Returns:
        - decorator (:obj:`Callable`): A class decorator.

    Examples:
        >>> class MyTreeValue(TreeValue):
        >>>     pass
        >>>
        >>> @utils_class(return_type=MyTreeValue)
        >>> class MyTreeUtils:
        >>>     @classmethod
        >>>     @classmethod_treelize()
        >>>     def add(cls, a, b):
        >>>         return a + b
        >>>
        >>> t1 = TreeValue({'a': 1, 'b': 2})
        >>> t2 = TreeValue({'a': 3, 'b': 4})
        >>> MyTreeUtils.add(t1, t2)  # MyTreeValue({'a': 4, 'b': 6})
    """
    return _class_config(
        return_type, False, False,
    )


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

    def _decorator(method):
        @wraps(method)
        def _new_method(cls, *args, **kwargs):
            rt = _auto_detect_type(cls) if return_type is AUTO_DETECT_RETURN_TYPE else return_type
            return func_treelize(mode, rt, inherit, missing, subside, rise)(partial(method, cls))(*args, **kwargs)

        return _new_method

    return _decorator
