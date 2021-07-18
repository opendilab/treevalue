from functools import partial
from typing import TypeVar, Type

_ClassType = TypeVar('_ClassType')


def init_magic(init_decorator):
    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        class _NewClass(clazz):
            def __init__(self, *args, **kwargs):
                init_decorator(partial(clazz.__init__, self))(*args, **kwargs)

        # noinspection PyTypeChecker
        return type(clazz.__name__, (_NewClass,), {})

    return _decorator
