from functools import wraps
from typing import Union, Any, Mapping

from ..common import BaseTree, Tree
from ...utils import init_magic, build_tree

_DATA_PROPERTY = '_property__data'
_PRESERVED_PROPERTIES = {
    _DATA_PROPERTY,
}


def get_data_property(t: 'TreeValue') -> BaseTree:
    return getattr(t, _DATA_PROPERTY)


def _dict_unpack(t: Union['TreeValue', Mapping[str, Any]]) -> Union[BaseTree, Any]:
    if isinstance(t, BaseTree):
        return t
    elif isinstance(t, TreeValue):
        return get_data_property(t)
    elif isinstance(t, dict):
        return Tree({str(key): _dict_unpack(value) for key, value in t.items()})
    else:
        return t


def _init_decorate(init_func):
    @wraps(init_func)
    def _new_init_func(data):
        if isinstance(data, (TreeValue, dict)):
            _new_init_func(_dict_unpack(data))
        elif isinstance(data, BaseTree):
            init_func(data)
        else:
            raise TypeError(
                "Unknown initialization type for tree value - {type}.".format(type=repr(type(data).__name__)))

    return _new_init_func


@init_magic(_init_decorate)
class TreeValue:
    """
    Overview:
        Base framework of tree value. \
        And if the fast functions and operators are what you need, \
        please use `FastTreeValue` in `treevalue.tree.general`. \
        The `TreeValue` class is a light-weight framework just for DIY.
    """

    def __init__(self, data: Union[BaseTree, 'TreeValue', dict]):
        """
        Overview:
            Constructor of `TreeValue`.

        Arguments:
            - data: (:obj:`Union[BaseTree, 'TreeValue', dict]`): Original data to init a tree value, \
                can be a `BaseTree`, `TreeValue` or dict.

        Example:
            >>> TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> # this is the tree:
            >>> # <root> -+--> a (1)
            >>> #         +--> b (2)
            >>> #         +--> x
            >>> #              +--> c (3)
            >>> #              +--> d (4)
        """
        setattr(self, _DATA_PROPERTY, data)

    @classmethod
    def __raw_value_to_value(cls, value):
        return cls(value) if isinstance(value, BaseTree) else value

    def __getattr__(self, key):
        """
        Overview:
            Get item from this tree value.

        Arguments:
            - key (:obj:`str`): Attribute name.

        Returns:
            - attr (:obj:): Target attribute value.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.a    # 1
            >>> t.b    # 2
            >>> t.x.c  # 3
        """
        _tree = get_data_property(self)
        if key in _tree.keys():
            value = get_data_property(self).__getitem__(key)
            return self.__raw_value_to_value(value)
        else:
            return self._attr_extern(key)

    def __setattr__(self, key, value):
        """
        Overview:
            Set sub node to this tree value.

        Arguments:
            - key (:obj:`str`): Attribute name.
            - value (:obj:): Sub value.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.a = 3                 # t will be TreeValue({'a': 3, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.b = {'x': 1, 'y': 2}  # t will be TreeValue({'a': 3, 'b': {'x': 1, 'y': 2}, 'x': {'c': 3, 'd': 4}})
        """
        if key in _PRESERVED_PROPERTIES:
            object.__setattr__(self, key, value)
        else:
            if isinstance(value, TreeValue):
                value = get_data_property(value)
            return get_data_property(self).__setitem__(key, value)

    def __delattr__(self, key):
        """
        Overview:
            Delete attribute from tree value.

        Arguments:
            - key (:obj:`str`): Attribute name.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t.a    # t will be TreeValue({'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t.x.c  # t will be TreeValue({'b': 2, 'x': {'d': 4}})
        """
        if key in _PRESERVED_PROPERTIES:
            raise AttributeError("Unable to delete attribute {attr}.".format(attr=repr(key)))
        else:
            return get_data_property(self).__delitem__(key)

    def __contains__(self, key) -> bool:
        """
        Overview:
            Check if attribute is in this tree value.

        Arguments:
            - key (:obj:`str`): Attribute name.

        Returns:
            - exist (:obj:`bool`): If attribute is in this tree value.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> 'a' in t  # True
            >>> 'b' in t  # True
            >>> 'c' in t  # False
        """
        return key in get_data_property(self).keys()

    def __iter__(self):
        """
        Overview:
            Get iterator of this tree value.

        Returns:
            - iter (:obj:`iter`): Iterator for keys and values.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': 3})
            >>> for key, value in t:
            >>>     print(key, value)

            The output will be:

            >>> a 1
            >>> b 2
            >>> x 3
        """
        for key, value in get_data_property(self).items():
            yield key, self.__raw_value_to_value(value)

    def __len__(self):
        """
        Overview:
            Get count of the keys.

        Returns:
            - length (:obj:`int`): Count of the keys.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> len(t)    # 3
            >>> len(t.x)  # 2
        """
        return len(get_data_property(self))

    def __bool__(self) -> bool:
        """
        Overview:
            Check if the tree value is not empty.

        Returns:
            - non_empty (:obj:`bool`): Not empty or do.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'e': {}})
            >>> not not t    # True
            >>> not not t.x  # True
            >>> not not t.e  # False
        """
        return not not get_data_property(self)

    def __repr__(self):
        """
        Overview:
            Get representation format of tree value.

        Returns:
            - repr (:obj:`str`): Representation string.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> repr(t)  # <TreeValue 0xffffffff keys: ['a', 'b', 'x']>, the is may be different
        """
        _tree = get_data_property(self)
        return "<{cls} {id} keys: {keys}>".format(
            cls=self.__class__.__name__,
            id=hex(id(_tree.actual())),
            keys=repr(sorted(_tree.keys()))
        )

    def __str__(self):
        """
        Overview:
            Get the structure of the tree.

        Returns:
            - str (:obj:`str`): Returned string.
        """
        return str(build_tree(
            self,
            repr_gen=lambda x: repr(x),
            iter_gen=lambda x: iter(x) if isinstance(x, TreeValue) else None,
        ))

    def __hash__(self):
        """
        Overview:
            Hash value of current object.

        Returns:
            - hash (:obj:`int`): Hash code of current object.
        """
        return hash(get_data_property(self))

    def __eq__(self, other):
        """
        Overview:
            Check the equality of two tree values.

        Arguments:
            - other (:obj:`TreeValue`): Another tree value.

        Returns:
            - equal (:obj:`bool`): Equality.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> clone(t) == t                                                # True
            >>> t == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 5}})      # False
            >>> t == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})      # True
            >>> t == FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})  # False (type not match)
        """
        if self is other:
            return True
        elif type(other) == self.__class__:
            return get_data_property(self) == get_data_property(other)
        else:
            return False

    def _attr_extern(self, key):
        """
        Overview:
            External protected function for support the unfounded attributes. \
            Default is raise a `KeyError`.

        Arguments:
            - key (:obj:`str`): Attribute name.

        Returns:
            - return (:obj:): Anything you like, \
                and if it is not able to validly return anything, \
                just raise an exception here.
        """
        raise KeyError("Attribute {key} not found.".format(key=repr(key)))

    def __setstate__(self, tree: Tree):
        """
        Overview:
            Deserialize operation, can support `pickle.loads`.

        Arguments:
            - tree (:obj:`Tree`): Deserialize tree.

        Examples:
            >>> import pickle
            >>> from treevalue import TreeValue
            >>>
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
            >>> bin_ = pickle.dumps(t)  # dump it to binary
            >>> pickle.loads(bin_)      #  TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
        """
        setattr(self, _DATA_PROPERTY, tree)

    def __getstate__(self):
        """
        Overview:
            Serialize operation, can support `pickle.dumps`.

        Examples:
            >>> import pickle
            >>> from treevalue import TreeValue
            >>>
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
            >>> bin_ = pickle.dumps(t)  # dump it to binary
            >>> pickle.loads(bin_)      #  TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
        """
        return getattr(self, _DATA_PROPERTY).actual()
