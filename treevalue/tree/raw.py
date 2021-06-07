from ..utils import StaticValueProxy, FinalMeta


class RawPackage(StaticValueProxy, metaclass=FinalMeta):
    pass


def raw_value(value) -> RawPackage:
    if isinstance(value, RawPackage):
        return value
    else:
        return RawPackage(value)


def raw_unpack(value):
    if isinstance(value, RawPackage):
        return value.value
    else:
        return value
