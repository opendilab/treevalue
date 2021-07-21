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
    """
    Overview:
        Decorate a int enum class with a new `loads` class method.

    Arguments:
        - enable_int (:obj:`bool`): Enable int parse, default is `True`.
        - value_preprocess (:obj:`Optional[Callable[[int, ], int]]`): Preprocessor of value, \
            default is `None` which means no change.
        - enable_str (:obj:`bool`): Enable str parse, default is `True`.
        - name_preprocess (:obj:`Optional[Callable[[str, ], str]]`): Preprocessor of name, \
            default is `None` which means no change.
        - external_process (:obj:`Optional[Callable[[Any, ], Optional[_EnumType]]]`): External processor \
            for the unprocessable data, default is `None` which means raise a `KeyError`.

    Examples:
        - Simple usage

        >>> from enum import IntEnum, unique
        >>>
        >>> @int_enum_loads()
        >>> @unique
        >>> class MyEnum(IntEnum):
        >>>     A = 1
        >>>     B = 2
        >>>
        >>> MyEnum.loads(1)    # MyEnum.A
        >>> MyEnum.loads('A')  # MyEnum.A
        >>> MyEnum.loads(2)    # MyEnum.B
        >>> MyEnum.loads('B')  # MyEnum.B
        >>> MyEnum.loads(-1)   # KeyError
        >>> MyEnum.loads('a')  # KeyError
        >>> MyEnum.loads('C')  # KeyError

        - Preprocessors

        >>> from enum import IntEnum, unique
        >>>
        >>> @int_enum_loads(name_preprocess=str.upper, value_preprocess=abs)
        >>> @unique
        >>> class MyEnum(IntEnum):
        >>>     A = 1
        >>>     B = 2
        >>>
        >>> MyEnum.loads(1)    # MyEnum.A
        >>> MyEnum.loads('A')  # MyEnum.A
        >>> MyEnum.loads(2)    # MyEnum.B
        >>> MyEnum.loads('B')  # MyEnum.B
        >>> MyEnum.loads(-1)   # MyEnum.A
        >>> MyEnum.loads('a')  # MyEnum.A
        >>> MyEnum.loads('C')  # KeyError

        - External processor

        >>> from enum import IntEnum, unique
        >>>
        >>> @int_enum_loads(external_process=lambda data: None)
        >>> @unique
        >>> class MyEnum(IntEnum):
        >>>     A = 1
        >>>     B = 2
        >>>
        >>> MyEnum.loads(1)    # MyEnum.A
        >>> MyEnum.loads('A')  # MyEnum.A
        >>> MyEnum.loads(2)    # MyEnum.B
        >>> MyEnum.loads('B')  # MyEnum.B
        >>> MyEnum.loads(-1)   # None
        >>> MyEnum.loads('a')  # None
        >>> MyEnum.loads('C')  # None
    """
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

        def _load_func(data) -> Optional[enum_class]:
            if isinstance(data, enum_class):
                return data
            elif enable_int and isinstance(data, int):
                return _int_value_to_item()[value_preprocess(data)]
            elif enable_str and isinstance(data, str):
                return _str_name_to_item()[name_preprocess(data)]
            else:
                return (external_process or _get_default_external_preprocess(enum_class))(data)

        def loads(cls, data) -> Optional[enum_class]:
            """
            Overview:
                Load enum data from raw data.

            Arguments:
                - data (:obj:`Any`): Data which going to be parsed.

            Returns:
                - enum_data (:obj:): Parsed enum data
            """
            return _load_func(data)

        enum_class.loads = classmethod(loads)
        return enum_class

    return _decorator
