from functools import wraps

from ..common import BaseTree, Tree
from ...utils import init_magic

_DATA_PROPERTY = '_property__data'
_PRESERVED_PROPERTIES = {
    _DATA_PROPERTY,
}


def _get_data_property(t: 'TreeValue') -> BaseTree:
    return getattr(t, _DATA_PROPERTY)


def _init_decorate(init_func):
    @wraps(init_func)
    def _new_init_func(data):
        if isinstance(data, TreeValue):
            _new_init_func(_get_data_property(data))
        elif isinstance(data, dict):
            _new_init_func(Tree(data))
        elif isinstance(data, Tree):
            init_func(data)
        else:
            raise TypeError(
                "Unknown initialization type for tree value - {type}.".format(type=repr(type(data).__name__)))

    return _new_init_func


@init_magic(_init_decorate)
class TreeValue:
    def __init__(self, data: BaseTree):
        setattr(self, _DATA_PROPERTY, data)

    def __getattr__(self, key):
        if key in _PRESERVED_PROPERTIES:
            return object.__getattribute__(key)
        else:
            return _get_data_property(self).__getitem__(key)

    def __setattr__(self, key, value):
        if key in _PRESERVED_PROPERTIES:
            object.__setattr__(self, key, value)
        else:
            return _get_data_property(self).__setattr__(key, value)

    def __delattr__(self, key):
        if key in _PRESERVED_PROPERTIES:
            raise AttributeError("Unable to delete attribute {attr}.".format(attr=repr(key)))
        else:
            return _get_data_property(self).__delattr__(key)
