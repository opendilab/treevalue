from functools import partial, wraps
from typing import TypeVar, Type

_ClassType = TypeVar('_ClassType')


def class_wraps(original_class: Type[_ClassType]):
    """
    Overview:
        Wrap class like functools.wraps, can be used in class decorators.

    Arguments:
        - original_class (:obj:`Type[_ClassType]`): Original class for wrapping.

    Example:
        >>> def cls_dec(clazz):
        >>>     @class_wraps(clazz)
        >>>     class _NewClazz(clazz):
        >>>         pass
        >>>
        >>>     return _NewClazz
    """

    # noinspection PyTypeChecker
    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        new_clazz = type(original_class.__name__, (clazz,), {
            '__doc__': original_class.__doc__,
            '__module__': original_class.__module__,
        })
        return new_clazz

    return _decorator


def init_magic(init_decorator):
    """
    Overview:
        Magic for initialization function of a class.

    Arguments:
        - init_decorator (:obj:`Callable`): Initialization function decorator.

    Example:
        >>> from functools import wraps
        >>>
        >>> def _init_dec(func):
        >>>     @wraps(func)
        >>>     def _new_func(value):
        >>>         func(value + 1)
        >>>
        >>>     return _new_func
        >>>
        >>> @init_magic(_init_dec)
        >>> class Container:
        >>>     def __init__(self, value):
        >>>         self.__value = value
        >>>
        >>>     @property
        >>>     def value(self):
        >>>         return self.__value
        >>>
        >>> c = Container(1)
        >>> c.value   # 2
        >>> c2 = Container(33)
        >>> c2.value  # 34
    """

    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        @class_wraps(clazz)
        class _NewClass(clazz):
            @wraps(clazz.__init__)
            def __init__(self, *args, **kwargs):
                init_decorator(partial(clazz.__init__, self))(*args, **kwargs)

        return _NewClass

    return _decorator
