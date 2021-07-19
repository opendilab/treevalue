from functools import partial
from typing import TypeVar, Type

_ClassType = TypeVar('_ClassType')


def class_wraps(original_class: Type[_ClassType]):
    # noinspection PyTypeChecker
    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        new_clazz = type(original_class.__name__, (clazz,), {
            '__doc__': original_class.__doc__,
            '__module__': original_class.__module__,
        })
        return new_clazz

    return _decorator


def init_magic(init_decorator):
    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        @class_wraps(clazz)
        class _NewClass(clazz):
            def __init__(self, *args, **kwargs):
                init_decorator(partial(clazz.__init__, self))(*args, **kwargs)

        return _NewClass

    return _decorator
