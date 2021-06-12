from enum import unique, IntEnum
from functools import wraps

from ..utils import int_enum_loads


@int_enum_loads(name_preprocess=lambda x: x.upper())
@unique
class TreeCalcMode(IntEnum):
    STRICT = 1
    LEFT = 2
    INNER = 3
    OUTER = 4


def treeilize():
    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            pass
            # return run_func(func, *args, **kwargs)

        return _new_func

    return _decorator
