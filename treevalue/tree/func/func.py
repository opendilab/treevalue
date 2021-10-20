from enum import IntEnum, unique
from functools import wraps
from typing import Type, TypeVar, Optional, Mapping, Union, Callable, Any

import enum_tools

from .cfunc import func_treelize
from ..tree import TreeValue
from ...utils import int_enum_loads, SingletonMark

TreeClassType_ = TypeVar("TreeClassType_", bound=TreeValue)


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


MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")

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
