class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ValueBasedSingletonMeta(type):
    _instances = {}

    def __call__(cls, value):
        key = (cls, value)
        if key not in cls._instances:
            cls._instances[key] = super(ValueBasedSingletonMeta, cls).__call__(value)
        return cls._instances[key]


class SingletonMark(metaclass=ValueBasedSingletonMeta):
    def __init__(self, mark):
        self.__mark = mark

    @property
    def mark(self):
        return self.__mark

    def __hash__(self):
        return hash(self.__mark)

    def __eq__(self, other):
        if other is self:
            return True
        elif type(other) == type(self):
            return other.__mark == self.__mark
        else:
            return False

    def __repr__(self):
        return "<{cls} {mark}>".format(
            cls=self.__class__.__name__,
            mark=repr(self.__mark),
        )
