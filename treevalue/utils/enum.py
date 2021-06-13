from enum import IntEnum, unique
from functools import lru_cache
from typing import Type, Optional, Callable, TypeVar, Any

_EnumType = TypeVar('_EnumType', bound=IntEnum)


def _default_value_preprocess(value: int):
    return value


def _default_name_preprocess(name: str):
    return name


def _get_default_external_preprocess(enum_class: Type[_EnumType]):
    def _default_external_preprocess(data):
        raise TypeError('Unknown type {type} for loads to {cls}.'.format(
            type=repr(type(data).__name__), cls=repr(enum_class.__name__),
        ))

    return _default_external_preprocess


def int_enum_loads(enable_int: bool = True, value_preprocess: Optional[Callable[[int, ], int]] = None,
                   enable_str: bool = True, name_preprocess: Optional[Callable[[str, ], str]] = None,
                   external_process: Optional[Callable[[Any, ], Optional[_EnumType]]] = None):
    value_preprocess = value_preprocess or _default_value_preprocess
    name_preprocess = name_preprocess or _default_name_preprocess

    def _decorator(enum_class: Type[_EnumType]):
        if not issubclass(enum_class, IntEnum):
            raise TypeError('Int enum expected but {type} found.'.format(type=repr(enum_class.__name__)))
        enum_class = unique(enum_class)

        @lru_cache()
        def _dict_item():
            return {key: value for key, value in enum_class.__members__.items()}

        @lru_cache()
        def _int_value_to_item():
            return {value.value: value for _, value in _dict_item().items()}

        @lru_cache()
        def _str_name_to_item():
            return {name_preprocess(key): value for key, value in _dict_item().items()}

        def loads(cls, data) -> Optional[enum_class]:
            if isinstance(data, enum_class):
                return data
            elif enable_int and isinstance(data, int):
                return _int_value_to_item()[value_preprocess(data)]
            elif enable_str and isinstance(data, str):
                return _str_name_to_item()[name_preprocess(data)]
            else:
                return (external_process or _get_default_external_preprocess(enum_class))(data)

        setattr(enum_class, 'loads', classmethod(loads))
        return enum_class

    return _decorator
