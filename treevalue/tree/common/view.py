from typing import List

from .base import BaseTree
from .tree import Tree


class TreeView(BaseTree):
    def __init__(self, tree: Tree, path: List[str]):
        self.__tree = tree
        self.__path = [str(segment) for segment in path]

    def __get_actual_tree(self) -> BaseTree:
        _tree = self.__tree
        for _segment in self.__path:
            _tree = _tree[_segment]

        if not isinstance(_tree, BaseTree):
            raise TypeError(
                'Viewed target is not a tree but {target} found.'.format(target=repr(type(_tree.__class__))))
        else:
            return _tree

    def __getitem__(self, key):
        return self.__get_actual_tree().__getitem__(key)

    def __setitem__(self, key, value):
        self.__get_actual_tree().__setitem__(key, value)

    def __delitem__(self, key):
        self.__get_actual_tree().__delitem__(key)

    def view(self, path: List[str]):
        return TreeView(self.__tree, self.__path + [str(segment) for segment in path])

    def clone(self):
        return self.__get_actual_tree().clone()

    def items(self):
        return self.__get_actual_tree().items()

    def keys(self):
        return self.__get_actual_tree().keys()

    def values(self):
        return self.__get_actual_tree().values()

    def actual(self):
        return self.__get_actual_tree().actual()
