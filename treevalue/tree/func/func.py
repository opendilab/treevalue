import warnings
from functools import wraps
from typing import Type, TypeVar, Optional, Mapping, Union, Callable, Any

from hbutils.design import SingletonMark

from .cfunc import MISSING_NOT_ALLOW
from .cfunc import func_treelize as _c_func_treelize
from ..tree import TreeValue

TreeClassType_ = TypeVar("TreeClassType_", bound=TreeValue)


def func_treelize(mode: str = 'strict', return_type: Optional[Type[TreeClassType_]] = TreeValue,
                  inherit: bool = True, missing: Union[Any, Callable] = MISSING_NOT_ALLOW, delayed: bool = False,
                  subside: Union[Mapping, bool, None] = None, rise: Union[Mapping, bool, None] = None):
    """
    Overview:
        Wrap a common function to tree-supported function.

    Arguments:
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inheriting in wrapped function, default is `True`.
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
        >>> @func_treelize()
        >>> def ssum(a, b):
        >>>     return a + b  # the a and b will be integers, not TreeValue
        >>>
        >>> t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        >>> ssum(1, 2)    # 3
        >>> ssum(t1, t2)  # TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 9}})
    """

    def _decorator(func):
        _treelized = _c_func_treelize(mode, return_type, inherit, missing, delayed, subside, rise)(func)

        @wraps(func)
        def _new_func(*args, **kwargs):
            return _treelized(*args, **kwargs)

        return _new_func

    return _decorator


#: Default value of the ``return_type`` arguments \
#: of ``method_treelize`` and ``classmethod_treelize``, \
#: which means return type will be auto configured to
#: the current class.
AUTO_DETECT_RETURN_TYPE = SingletonMark("auto_detect_return_type")


def method_treelize(mode: str = 'strict', return_type: Optional[Type[TreeClassType_]] = AUTO_DETECT_RETURN_TYPE,
                    inherit: bool = True, missing: Union[Any, Callable] = MISSING_NOT_ALLOW, delayed: bool = False,
                    subside: Union[Mapping, bool, None] = None, rise: Union[Mapping, bool, None] = None,
                    self_copy: bool = False):
    """
    Overview:
        Wrap a common instance method to tree-supported method.

    Attention:
        - This decorator can only used to instance method, usage with class method may cause unconditional fatal.
        - When decorated instance method is called, the `self` argument will be no longer the class instance, \
            but the single element of the tree instead.

    Arguments:
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, \
            default is `AUTO_DETECT_RETURN_VALUE`, which means automatically use the decorated method's class.
        - inherit (:obj:`bool`): Allow inheriting in wrapped function, default is `True`.
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
    if return_type is AUTO_DETECT_RETURN_TYPE:
        def _get_self_class(self):
            return self.__class__
    else:
        def _get_self_class(self):
            return return_type

    if self_copy and rise is not None:
        warnings.warn(UserWarning(f'The rise configuration {repr(rise)} will be ignored '
                                  f'due to the enable of the self_copy option.'), stacklevel=2)
        rise = None

    def _decorator(method):
        _treelized = _c_func_treelize(mode, _get_self_class, inherit, missing, delayed, subside, rise)(method)

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


def classmethod_treelize(mode: str = 'strict', return_type: Optional[Type[TreeClassType_]] = AUTO_DETECT_RETURN_TYPE,
                         inherit: bool = True, missing: Union[Any, Callable] = MISSING_NOT_ALLOW, delayed: bool = False,
                         subside: Union[Mapping, bool, None] = None, rise: Union[Mapping, bool, None] = None):
    """
    Overview:
        Wrap a common class method to tree-supported method.

    Attention:
        - This decorator can only used to class method, usage with instance method may cause unconditional fatal.
        - When decorated instance method is called, the `cls` argument will still be the calling class.

    Arguments:
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, \
            default is `AUTO_DETECT_RETURN_VALUE`, which means automatically use the decorated method's class.
        - inherit (:obj:`bool`): Allow inheriting in wrapped function, default is `True`.
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

    return func_treelize(mode, _get_cls_class, inherit, missing, delayed, subside, rise)
