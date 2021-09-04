from typing import List, Union, Callable, Any

from .base import BaseTree
from .tree import Tree


class TreeView(BaseTree):
    """
    Overview:
        Tree view data model, based on `BaseTree`.
    """

    def __init__(self, tree: Tree, path: List[str]):
        """
        Overview:
            Constructor of `TreeValue`.

        Arguments:
            - tree (:obj:`Tree`): Based tree.
            - path (:obj:`List[str]`): Viewing path.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> tv = t.view(["x"])                # tv should be equal to Tree({'c': 3, 'd': 4})
            >>> t['x'] = Tree({'c': 5, 'd': 6})
            >>> tv                                # tv should be equal to Tree({'c': 5, 'd': 6})
        """
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

    def clone(self, copy_value: Union[None, bool, Callable, Any] = None):
        return self.__get_actual_tree().clone(copy_value)

    def copy_from(self, other: 'BaseTree'):
        self.actual().copy_from(other.actual())
        return self

    def items(self):
        return self.__get_actual_tree().items()

    def keys(self):
        return self.__get_actual_tree().keys()

    def values(self):
        return self.__get_actual_tree().values()

    def actual(self) -> Tree:
        return self.__get_actual_tree().actual()
