from functools import wraps
from typing import Union

from ..common import BaseTree, Tree
from ...utils import init_magic

_DATA_PROPERTY = '_property__data'
_PRESERVED_PROPERTIES = {
    _DATA_PROPERTY,
}


def get_data_property(t: 'TreeValue') -> BaseTree:
    return getattr(t, _DATA_PROPERTY)


def _init_decorate(init_func):
    @wraps(init_func)
    def _new_init_func(data):
        if isinstance(data, TreeValue):
            _new_init_func(get_data_property(data))
        elif isinstance(data, dict):
            _new_init_func(Tree({
                str(key): get_data_property(value) if isinstance(value, TreeValue) else value
                for key, value in data.items()
            }))
        elif isinstance(data, BaseTree):
            init_func(data)
        else:
            raise TypeError(
                "Unknown initialization type for tree value - {type}.".format(type=repr(type(data).__name__)))

    return _new_init_func


@init_magic(_init_decorate)
class TreeValue:
    def __init__(self, data: Union[BaseTree, 'TreeValue', dict]):
        setattr(self, _DATA_PROPERTY, data)

    def __getattr__(self, key):
        if key in _PRESERVED_PROPERTIES:
            return object.__getattribute__(self, key)
        else:
            _tree = get_data_property(self)
            if key in _tree.keys():
                value = get_data_property(self).__getitem__(key)
                return self.__class__(value) if isinstance(value, BaseTree) else value
            else:
                self._attr_extern(key)

    def __setattr__(self, key, value):
        if key in _PRESERVED_PROPERTIES:
            object.__setattr__(self, key, value)
        else:
            if isinstance(value, TreeValue):
                value = get_data_property(value)
            return get_data_property(self).__setitem__(key, value)

    def __delattr__(self, key):
        if key in _PRESERVED_PROPERTIES:
            raise AttributeError("Unable to delete attribute {attr}.".format(attr=repr(key)))
        else:
            return get_data_property(self).__delitem__(key)

    def __contains__(self, item):
        return item in get_data_property(self).keys()

    def __repr__(self):
        _tree = get_data_property(self)
        return "<{cls} {id} keys: {keys}>".format(
            cls=self.__class__.__name__,
            id=hex(id(_tree.actual())),
            keys=repr(sorted(_tree.keys()))
        )

    def __hash__(self):
        return hash(get_data_property(self))

    def __eq__(self, other):
        if self is other:
            return True
        elif type(other) == self.__class__:
            return get_data_property(self) == get_data_property(other)
        else:
            return False

    def _attr_extern(self, key):
        raise KeyError("Attribute {key} not found.".format(key=repr(key)))
