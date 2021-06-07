from enum import unique, Enum

from .key import _check_key_format
from .raw import raw_unpack, raw_value


@unique
class NodeType(Enum):
    VALUE = 1
    TREE = 2


_PRESERVED_ATTRS = {
    '_dict'
}


class TreeMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.__registered__ = {}
        cls.__default_output_class__ = cls

    def check_key(cls, key):
        return _check_key_format(key)

    def check_value(cls, value):
        return value

    def register(cls, name, method):
        cls.__registered__[name] = method

    def unregister(cls, name):
        del cls.__registered__[name]


class TreeValue(metaclass=TreeMeta):
    def __init__(self, data):
        data = data or {}
        if isinstance(data, dict):
            _dict = dict(data)
        elif type(data) == self.__class__:
            _dict = data.json()
        else:
            raise TypeError('Unknown data type - {type}.'.format(type=repr(type(data).__name__)))

        self._dict = {}
        for key, value in _dict.items():
            _key = self.__class__.check_key(key)
            _value = self.__loads(value)
            _type, _real_value = self.__unpack_value(_value)
            if _type == NodeType.VALUE:
                _real_value = self.__class__.check_value(_real_value)
            self._dict[_key] = (_type, _real_value)

    @classmethod
    def __loads(cls, data):
        if type(data) == cls:
            return data
        elif isinstance(data, dict):
            return cls(data)
        else:
            return data

    def __getattr__(self, item):
        if item in _PRESERVED_ATTRS:
            return super().__getattribute__(item)
        elif self.__class__.check_key(item) in self._dict.keys():
            return self.__get_attr(item)
        elif item in self.__registered__.keys():
            return self.__get_func_tree(self.__registered__[item])
        else:
            return self.__get_property(item)

    def __setattr__(self, key, value):
        if key in _PRESERVED_ATTRS:
            return super().__setattr__(key, value)
        else:
            return self.__set_attr(key, value)

    def __delattr__(self, item):
        if item in _PRESERVED_ATTRS:
            return super().__delattr__(item)
        else:
            return self.__del_attr(item)

    def __get_attr(self, key):
        _type, _value = self._dict[self.__class__.check_key(key)]
        return _value

    def __set_attr(self, key, value):
        self._dict[self.__class__.check_key(key)] = self.__unpack_value(value)

    def __del_attr(self, key):
        del self._dict[self.__class__.check_key(key)]

    def __get_func_tree(self, func):
        raise NotImplementedError

    def __get_property(self, item):
        raise NotImplementedError

    @classmethod
    def __unpack_value(cls, value):
        if type(value) == cls:
            return NodeType.TREE, value
        else:
            return NodeType.VALUE, raw_unpack(value)

    @classmethod
    def __pack_value(cls, type_: NodeType, value):
        if type_ == NodeType.TREE:
            if type(value) == cls:
                return value
            else:
                raise TypeError('Not a valid tree - {cls} expected but {type} found.'.format(
                    cls=repr(cls.__name__), type=repr(type(value).__name__),
                ))
        elif type_ == NodeType.VALUE:
            if type(value) == cls:
                return raw_value(value)
            else:
                return value
        else:
            raise ValueError('Unknown value type - {value}.'.format(value=repr(type_)))

    def _structure(self, structure: bool = False):
        _result = {}
        for key, (_type, _value) in self._dict.items():
            if _type == NodeType.VALUE:
                _result[key] = None if structure else _value
            else:
                _result[key] = getattr(_value, '_structure')(structure)

        return _result

    def json(self):
        return self._structure(structure=False)

    def keys(self):
        for key, _ in self.items():
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def items(self):
        for key, value in sorted(self._dict.items()):
            yield key, value
