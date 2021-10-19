# distutils:language=c++
# cython:language_level=3

import cython

from ..common.storage cimport TreeStorage, create_storage
from ...utils import build_tree

cdef inline TreeStorage _dict_unpack(dict d):
    cdef str k
    cdef object v
    cdef dict result = {}

    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _dict_unpack(v)
        elif isinstance(v, TreeValue):
            result[k] = v._detach()
        else:
            result[k] = v

    return create_storage(result)

cdef class TreeValue:
    r"""
    Overview:
        Base framework of tree value. \
        And if the fast functions and operators are what you need, \
        please use `FastTreeValue` in `treevalue.tree.general`. \
        The `TreeValue` class is a light-weight framework just for DIY.
    """

    @cython.binding(True)
    def __init__(self, object data):
        """
        Overview:
            Constructor of `TreeValue`.

        Arguments:
            - data: (:obj:`Union[TreeStorage, 'TreeValue', dict]`): Original data to init a tree value, \
                can be a `TreeStorage`, `TreeValue` or dict.

        Example:
            >>> TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> # this is the tree:
            >>> # <root> -+--> a (1)
            >>> #         +--> b (2)
            >>> #         +--> x
            >>> #              +--> c (3)
            >>> #              +--> d (4)
        """
        if isinstance(data, TreeStorage):
            self._st = data
        elif isinstance(data, TreeValue):
            self._st = data._detach()
        elif isinstance(data, dict):
            self._st = _dict_unpack(data)
        else:
            raise TypeError(
                "Unknown initialization type for tree value - {type}.".format(
                    type=repr(type(data).__name__)))

        self._type = type(self)

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return ({},), {}

    cpdef TreeStorage _detach(self):
        return self._st

    cdef inline object _unraw(self, object obj):
        if isinstance(obj, TreeStorage):
            return self._type(obj)
        else:
            return obj

    cdef inline object _raw(self, object obj):
        if isinstance(obj, TreeValue):
            return obj._detach()
        else:
            return obj

    @cython.binding(True)
    cpdef _attr_extern(self, str key):
        r"""
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
        raise AttributeError("Attribute {key} not found.".format(key=repr(key)))

    @cython.binding(True)
    def __getattr__(self, str item):
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
        try:
            return self._unraw(self._st.get(item))
        except KeyError:
            return self._attr_extern(item)

    @cython.binding(True)
    def __setattr__(self, str key, object value):
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
        self._st.set(key, self._raw(value))

    @cython.binding(True)
    def __delattr__(self, str item):
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
        try:
            self._st.del_(item)
        except KeyError:
            raise AttributeError("Unable to delete attribute {attr}.".format(attr=repr(item)))

    @cython.binding(True)
    def __contains__(self, str item):
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
        return self._st.contains(item)

    @cython.binding(True)
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
        cdef str k
        cdef object v
        for k, v in self._st.items():
            yield k, self._unraw(v)

    @cython.binding(True)
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
        return self._st.size()

    @cython.binding(True)
    def __bool__(self):
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
        return not self._st.empty()

    @cython.binding(True)
    cpdef str _repr(self):
        return f'<{self.__class__.__name__} {hex(id(self._st))}>'

    @cython.binding(True)
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
        return str(build_tree(
            self,
            repr_gen=lambda x: x._repr() if isinstance(x, TreeValue) else repr(x),
            iter_gen=lambda x: iter(x) if isinstance(x, TreeValue) else None,
        ))

    @cython.binding(True)
    def __hash__(self):
        """
        Overview:
            Hash value of current object.

        Returns:
            - hash (:obj:`int`): Hash code of current object.
        """
        return hash(self._st)

    @cython.binding(True)
    def __eq__(self, object other):
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
        elif type(other) == self._type:
            return self._st == other._detach()
        else:
            return False

    @cython.binding(True)
    def __setstate__(self, TreeStorage state):
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
        self._st = state
        self._type = type(self)

    @cython.binding(True)
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
        return self._st