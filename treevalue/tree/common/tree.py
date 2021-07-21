from functools import wraps
from typing import Dict, Any, Union, List

from .base import BaseTree
from ...utils import init_magic


def _to_tree_decorator(init_func):
    @wraps(init_func)
    def _new_init_func(data):
        if isinstance(data, BaseTree):
            _new_init_func(data.json())
        elif isinstance(data, dict):
            init_func({
                str(key): Tree(value) if isinstance(value, dict) else value
                for key, value in data.items()
            })
        else:
            raise TypeError(
                "Dict value expected for dispatch value but {type} actually.".format(type=repr(type(data).__name__)))

    return _new_init_func


@init_magic(_to_tree_decorator)
class Tree(BaseTree):
    """
    Overview:
        Tree node data model, based on `BaseTree`.
    """

    def __init__(self, data: Union[Dict[str, Union['Tree', Any]], 'Tree']):
        """
        Overview:
            Constructor of `Tree`, can be `dict`, `Tree`, `TreeView`.
            When dict passed in, a new tree structure will be created once.
            When `Tree` or `TreeView` passed in, a fully copy will be constructed in this object.

        Arguments:
            - data (:obj:`Union[Dict[str, Union['Tree', Any]], 'Tree']`): Any data can be parsed into `Tree`.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})  # t is a new tree structure
            >>> t2 = Tree(t)                                       # t2 is a full copy of t1
            >>> t3 = Tree({'a': t, 'b': t2})                       # t3 is a tree with subtree of t and t2 (not copy)
        """
        self.__dict = data

    def __check_key_exist(self, key):
        if key not in self.__dict.keys():
            raise KeyError("Key {key} not found.".format(key=repr(key)))

    def __getitem__(self, key):
        self.__check_key_exist(key)
        return self.__dict[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = Tree(value)
        self.__dict[key] = value

    def __delitem__(self, key):
        self.__check_key_exist(key)
        del self.__dict[key]

    def view(self, path: List[str]):
        from .view import TreeView
        return TreeView(self, path)

    def clone(self):
        return self.__class__(self)

    def items(self):
        return self.__dict.items()

    def keys(self):
        return self.__dict.keys()

    def values(self):
        return self.__dict.values()

    def actual(self):
        return self
