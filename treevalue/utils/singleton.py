class SingletonMeta(type):
    """
    Overview:
        Meta class for singleton mode.

    Example:
        >>> class MyService(metaclass=SingletonMeta):
        >>>     def get_value(self):
        >>>         return 233
        >>>
        >>> s = MyService()
        >>> s.get_value()    # 233
        >>> s1 = MyService()
        >>> s1 is s          # True
    """
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__()
        return cls._instances[cls]


class ValueBasedSingletonMeta(type):
    """
    Overview:
        Meta class for value based singleton mode.

    Example:
        >>> class MyData(metaclass=ValueBasedSingletonMeta):
        >>>     def __init__(self, value):
        >>>         self.__value = value
        >>>
        >>>     @property
        >>>     def value(self):
        >>>         return self.__value
        >>>
        >>> d1 = MyData(1)
        >>> d1.value       # 1
        >>> d2 = MyData(1)
        >>> d3 = MyData(2)
        >>> d2 is d1       # True
        >>> d2 is d3       # False
    """
    _instances = {}

    def __call__(cls, value):
        key = (cls, value)
        if key not in cls._instances:
            cls._instances[key] = super(ValueBasedSingletonMeta, cls).__call__(value)
        return cls._instances[key]


class SingletonMark(metaclass=ValueBasedSingletonMeta):
    """
    Overview:
        Singleton mark for some situation.
        Can be used when some default value is needed, especially when `None` has meaning which is not default.

    Example:
        >>> NO_VALUE = SingletonMark("no_value")
        >>> NO_VALUE is SingletonMark("no_value")  # True
    """

    def __init__(self, mark):
        self.__mark = mark

    @property
    def mark(self):
        """
        Overview:
            Get mark string of this mark object.

        Returns:
            - mark (:obj:`str`): Mark string
        """
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
