from abc import ABCMeta, abstractmethod
from typing import List, Union, Callable, Any

from treevalue.utils import build_tree


class BaseTree(metaclass=ABCMeta):
    """
    Overview:
        Base abstract structure of a tree data class.
    """

    @abstractmethod
    def __getitem__(self, key):
        """
        Overview:
            Get item from this tree node, raw value and tree node returns.

        Arguments:
            - key (:obj:`str`): Key of the sub tree node.

        Returns:
            - return (:obj:`Any`): Tree node or raw value (if the sub node is value node).

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t['a']       # 1
            >>> t['x']       # Tree({'c': 3, 'd': 4})
            >>> t['x']['c']  # 3
        """

        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __setitem__(self, key, value):
        """
        Overview:
            Set item to this tree node, raw value and tree node supported.

        Arguments:
            - key (:obj:`str`): Key of the sub tree node.
            - value (:obj:`Any`): Given mode or value to be set.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t['a'] = 3
            >>> t  # Tree({'a': 3, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t['x']['e'] = 10
            >>> t  # Tree({'a': 3, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 10}})
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __delitem__(self, key):
        """
        Overview:
            Delete item from this tree node.

        Arguments:
            - key (:obj:`str`): Key of the sub tree node.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t['a']
            >>> t  # Tree({'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t['x']['c']
            >>> t  # Tree({'b': 2, 'x': {'d': 4}})
        """
        raise NotImplementedError  # pragma: no cover

    def json(self):
        """
        Overview:
            Get full json data of this tree.

        Returns:
            - json (:obj:`dict`): Json data

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.json()  # {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
        """
        return {
            key: value.json() if isinstance(value, BaseTree) else value
            for key, value in self.items()
        }

    @abstractmethod
    def view(self, path: List[str]):
        """
        Overview:
            Get view of the current tree.

        Arguments:
            - path (:obj:`List[str]`): Viewing path.

        Returns:
            - viewed_tree (:obj:`TreeView`): Viewed tree.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t1 = t['x']
            >>> t2 = t.view(["x"])
            >>>
            >>> t1['c']  # 3
            >>> t2['c']  # 3
            >>>
            >>> t.x = Tree({'c': 5, 'd': 6})
            >>> t1['c']  # 3
            >>> t2['c']  # 5
        """

        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def clone(self, copy_value: Union[None, bool, Callable, Any] = None):
        """
        Overview:
            Fully clone this tree.

        Arguments:
            - copy_value (:obj:`Union[None, bool, Callable, Any]`): Deep copy value or not, \
                default is `None` which means do not deep copy the values. \
                If deep copy is required, just set it to `True`.

        Returns:
            - cloned (:obj:`Tree`): Cloned new tree.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t2 = t.clone()
            >>> t2                 # Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t2 is t            # False
            >>> t2['x'] is t['x']  # False
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def copy_from(self, other: 'BaseTree'):
        """
        Overview:
            Copy data from another tree.

        Arguments:
            - other (:obj:`BaseTree`): Another target tree.

        Returns:
            - self (:obj:`BaseTree`): Self object

        Example:
            >>> # todo, complete this demo
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def items(self):
        """
        Overview:
            Get item iterator of this tree node.

        Returns:
            - iter (:obj:`iter`): Item iterator of this tree node.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> for key, value in t.items():
            >>>     print(key, value)

            The output should be

            >>> a 1
            >>> b 2
            >>> x <Tree 0x7f74f6daaf60 keys: ['c', 'd']>
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def keys(self):
        """
        Overview:
            Get key iterator of this tree node.

        Returns:
            - iter (:obj:`iter`): Key iterator of this tree node.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> for key in t.keys():
            >>>     print(key)

            The output should be

            >>> a
            >>> b
            >>> x
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def values(self):
        """
        Overview:
            Get value iterator of this tree node.

        Returns:
            - iter (:obj:`iter`): Value iterator of this tree node.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> for value in t.values():
            >>>     print(value)

            The output should be

            >>> 1
            >>> 2
            >>> <Tree 0x7f74f6daaf60 keys: ['c', 'd']>
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def actual(self):
        """
        Overview:
            Get actual tree node of current tree object.
            If this is a `Tree` object, just return itself.
            If this is a `TreeView` object, it will return the actually viewed tree node.

        Returns:
            - actual (:obj:`Tree`): Actual tree node.
        """
        raise NotImplementedError  # pragma: no cover

    def __len__(self):
        return len(self.keys())

    def __bool__(self):
        return len(self.keys()) > 0

    def __hash__(self):
        return hash(tuple([(key, value) for key, value in sorted(self.items())]))

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, BaseTree):
            if set(self.keys()) == set(other.keys()):
                for key in self.keys():
                    if self[key] != other[key]:
                        return False
                return True
            else:
                return False
        else:
            return False

    def __repr__(self):
        return '<{cls} {id} keys: {keys}>'.format(
            cls=self.__class__.__name__,
            id=hex(id(self.actual())),
            keys=repr(sorted(self.keys()))
        )

    def __str__(self):
        """
        Overview:
            Return tree-formatted string.

        Returns:
            - string (:obj:`str`): Tree-formatted string.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'z': [1, 2], 'v': raw({'1': '2'})})
            >>> print(t)

            The output will be

            >>> <Tree 0x7f9fa48b9588 keys: ['a', 'b', 'v', 'x', 'z']>
            >>> ├── 'a' --> 1
            >>> ├── 'b' --> 2
            >>> ├── 'v' --> {'1': '2'}
            >>> ├── 'x' --> <Tree 0x7f9fa48b95c0 keys: ['c', 'd']>
            >>> │   ├── 'c' --> 3
            >>> │   └── 'd' --> 4
            >>> └── 'z' --> [1, 2]
        """
        return str(build_tree(self, repr_gen=lambda value: repr(value)))
