class FinalMeta(type):
    def __new__(mcs, name, bases, attrs):
        for b in bases:
            if isinstance(b, FinalMeta):
                raise TypeError("Type {name} is a final class, which is not an acceptable base type."
                                .format(name=repr(b.__name__)))
        return type.__new__(mcs, name, bases, attrs)
