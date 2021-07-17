from enum import unique, IntEnum

from ....utils import int_enum_loads


@int_enum_loads(name_preprocess=lambda x: x.upper())
@unique
class TreeCalcMode(IntEnum):
    STRICT = 1
    LEFT = 2
    INNER = 3
    OUTER = 4
