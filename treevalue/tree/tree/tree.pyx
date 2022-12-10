# distutils:language=c++
# cython:language_level=3

import os
from collections.abc import Sized, Container, Reversible, Mapping
from operator import itemgetter

import cython
from hbutils.design import SingletonMark

from .constraint cimport Constraint, to_constraint, transact, _EMPTY_CONSTRAINT
from ..common.delay cimport undelay, _c_delayed_partial, DelayedProxy
from ..common.storage cimport TreeStorage, create_storage, _c_undelay_data
from ...utils import format_tree

cdef class _CObject:
    pass

try:
    reversed({'a': 1}.keys())
except TypeError:
    _reversible = False
else:
    _reversible = True

cdef inline object _item_unwrap(object v):
    if isinstance(v, list) and len(v) == 1:
        return v[0]
    else:
        return v

_GET_NO_DEFAULT = SingletonMark('get_no_default')

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

_DEFAULT_STORAGE = create_storage({})

cdef class _SimplifiedConstraintProxy:
    def __cinit__(self, Constraint cons):
        self.cons = cons

cdef inline Constraint _c_get_constraint(object cons):
    if isinstance(cons, _SimplifiedConstraintProxy):
        return cons.cons
    else:
        return to_constraint(cons)

cdef class ValidationError(Exception):
    def __init__(self, TreeValue obj, Exception error, tuple path, Constraint cons):
        Exception.__init__(self, obj, error, path, cons)
        self._object = obj
        self._error = error
        self._path = path
        self._cons = cons

    def __str__(self):
        return f"Validation failed on {self._cons!r} at position {self._path!r}{os.linesep}" \
               f"{type(self._error).__name__}: {self._error}"

cdef class TreeValue:
    r"""
    Overview:
        Base framework of tree value. \
        And if the fast functions and operators are what you need, \
        please use `FastTreeValue` in `treevalue.tree.general`. \
        The `TreeValue` class is a light-weight framework just for DIY.
    """

    def __cinit__(self, object data, object constraint=None):
        self._st = _DEFAULT_STORAGE
        self.constraint = _EMPTY_CONSTRAINT
        self._type = type(self)
        self._child_constraints = {}

    @cython.binding(True)
    def __init__(self, object data, object constraint=None):
        """
        Constructor of :class:`TreeValue`.

        :param data: Original data to init a tree value, should be a :class:`treevalue.tree.common.TreeStorage`, \
            :class:`TreeValue` or a :class:`dict`.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})  # create an instance
            >>> t
            <TreeValue 0x7fbcf70750b8>
            ├── 'a' --> 1
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fbcf70750f0>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> t2 = TreeValue(t)  # create a new treevalue with the same storage of t
            >>> t2
            <TreeValue 0x7fbcf70750b8>
            ├── 'a' --> 1
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fbcf70750f0>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> t2 is t
            False
        """
        if isinstance(data, TreeStorage):
            self._st = data
            self.constraint = _c_get_constraint(constraint)
        elif isinstance(data, TreeValue):
            self._st = data._detach()
            if constraint is None:
                self.constraint = data.constraint
                self._child_constraints = data._child_constraints
            else:
                self.constraint = _c_get_constraint(constraint)
        elif isinstance(data, dict):
            self._st = _dict_unpack(data)
            self.constraint = _c_get_constraint(constraint)
        else:
            raise TypeError(
                "Unknown initialization type for tree value - {type}.".format(
                    type=repr(type(data).__name__)))

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return ({},), {}

    @cython.binding(True)
    cpdef TreeStorage _detach(self):
        """
        Detach the inner :class:`treevalue.tree.common.TreeStorage` object.

        :return: :class:`treevalue.tree.common.TreeStorage` object.

        .. warning::
            This is an inner method of :class:`TreeValue`, which is not recommended to be actually used. \
            If you need to instantiate a new :class:`TreeValue` with the same storage, just pass this \
            :class:`TreeValue` object as the argument of the :meth:`__init__`.
        """
        return self._st

    cdef inline object _unraw(self, object obj, str key):
        cdef _SimplifiedConstraintProxy child_constraint
        if isinstance(obj, TreeStorage):
            if key in self._child_constraints:
                child_constraint = self._child_constraints[key]
            else:
                child_constraint = _SimplifiedConstraintProxy(transact(self.constraint, key))
                self._child_constraints[key] = child_constraint
            return self._type(obj, constraint=child_constraint)
        else:
            return obj

    cdef inline object _raw(self, object obj):
        if isinstance(obj, TreeValue):
            return obj._detach()
        else:
            return obj

    @cython.binding(True)
    cpdef get(self, str key, object default=None):
        r"""
        Get item from the tree node.

        :param key: Item's name.
        :param default: Default value when this item is not found, default is ``None``.
        :return: Item's value.

        .. note::
            The method :meth:`get` will never raise ``KeyError``, like the behaviour in \
            `dict.get <https://docs.python.org/3/library/stdtypes.html#dict.get>`_.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.get('a')
            1
            >>> t.get('x')
            <TreeValue 0x7f488a65f0b8>
            ├── 'c' --> 3
            └── 'd' --> 4
            >>> t.get('f')  # key not exist
            None
            >>> t.get('f', 123)
            123
        """
        return self._unraw(self._st.get_or_default(key, default), key)

    @cython.binding(True)
    cpdef pop(self, str key, object default=_GET_NO_DEFAULT):
        """
        Pop item from the tree node.

        :param key: Item's name.
        :param default: Default value when this item is not found, default is ``_GET_NO_DEFAULT`` which means \
            just raise ``KeyError`` when not found.
        :return: Item's value.
        :raise KeyError: When ``key`` is not exist and ``default`` is not given, raise ``KeyError``.

        .. note::
            The method :meth:`pop` will raise ``KeyError`` when ``key`` is not found, like the behaviour in \
            `dict.pop <https://docs.python.org/3/library/stdtypes.html#dict.pop>`_.
        
        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.pop('a')
            1
            >>> t.pop('x')
            <TreeValue 0x7f488a65f080>
            ├── 'c' --> 3
            └── 'd' --> 4
            >>> t
            <TreeValue 0x7f488a65f048>
            └── 'b' --> 2
            >>> t.pop('f')
            KeyError: 'f'
            >>> t.pop('f', 123)
            123
        """
        cdef object value
        if default is _GET_NO_DEFAULT:
            value = self._st.pop(key)
        else:
            value = self._st.pop_or_default(key, default)

        return self._unraw(value, key)

    @cython.binding(True)
    cpdef popitem(self):
        """
        Pop item (with a key and its value) from the tree node.

        :return: Popped item.
        :raise KeyError: When current treevalue is empty.

        .. note::
            The method :meth:`popitem` will raise ``KeyError`` when empty, like the behaviour in \
            `dict.popitem <https://docs.python.org/3/library/stdtypes.html#dict.popitem>`_.
        
        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.popitem()
            ('x', <TreeValue 0x7f488a65f0b8>
            ├── 'c' --> 3
            └── 'd' --> 4
            )
            >>> t.popitem()
            ('b', 2)
            >>> t.popitem()
            ('a', 1)
            >>> t.popitem()
            KeyError: 'popitem(): TreeValue is empty.'
        """
        cdef str k
        cdef object v
        try:
            k, v = self._st.popitem()
            return k, self._unraw(v, k)
        except KeyError:
            raise KeyError(f'popitem(): {self._type.__name__} is empty.')

    @cython.binding(True)
    cpdef void clear(self):
        """
        Clear all the items in this treevalue object.
        
        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t
            <TreeValue 0x7fd2553f0048>
            ├── 'a' --> 1
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fd2553e3fd0>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> t.clear()
            >>> t
            <TreeValue 0x7fd2553f0048>
        """
        self._st.clear()

    @cython.binding(True)
    cpdef object setdefault(self, str key, object default=None):
        """
        Set the ``default`` to this treevalue and return it if the ``key`` is not exist, \
        otherwise just return the existing value of ``key``.

        :param key: Items' name.
        :param default: Default value of the ``key``, ``None`` will be used when not given.
        :return: The newest value of the ``key``.

        .. note::
            The behaviour of method :meth:`setdefault` is similar to \
            `dict.setdefault <https://docs.python.org/3/library/stdtypes.html#dict.setdefault>`_.

        Examples:
            >>> from treevalue import TreeValue, delayed
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.setdefault('d', 'dsflgj')  # set new value
            'dsflgj'
            >>> t
            <TreeValue 0x7efe31576048>
            ├── 'a' --> 1
            ├── 'b' --> 3
            ├── 'c' --> '233'
            └── 'd' --> 'dsflgj'
            >>> t.setdefault('ff')  # default value - None
            >>> t
            <TreeValue 0x7efe31576048>
            ├── 'a' --> 1
            ├── 'b' --> 3
            ├── 'c' --> '233'
            ├── 'd' --> 'dsflgj'
            └── 'ff' --> None
            >>> t.setdefault('a', 1000)  # existing key
            1
            >>> t
            <TreeValue 0x7efe31576048>
            ├── 'a' --> 1
            ├── 'b' --> 3
            ├── 'c' --> '233'
            ├── 'd' --> 'dsflgj'
            └── 'ff' --> None
            >>> t.setdefault('g', delayed(lambda: 1))  # delayed value
            1
            >>> t
            <TreeValue 0x7efe31576048>
            ├── 'a' --> 1
            ├── 'b' --> 3
            ├── 'c' --> '233'
            ├── 'd' --> 'dsflgj'
            ├── 'ff' --> None
            └── 'g' --> 1
        """
        return self._unraw(self._st.setdefault(key, self._raw(default)), key)

    cdef inline void _update(self, object d, dict kwargs) except*:
        cdef object dt
        if d is None:
            dt = {}
        elif isinstance(d, Mapping):
            dt = d
        elif isinstance(d, TreeValue):
            dt = d._detach().detach()
        elif isinstance(d, TreeStorage):
            dt = d.detach()
        else:
            raise TypeError(f'Invalid type of update dict - {type(d)!r}.')

        cdef str key
        cdef object value
        for key, value in dt.items():
            self._st.set(key, self._raw(value))
        for key, value in kwargs.items():
            self._st.set(key, self._raw(value))

    @cython.binding(True)
    def update(self, __update_dict=None, **kwargs):
        """
        Overview:
            Update items in current treevalue.

        :param __update_dict: Dictionary object for updating.
        :param kwargs: Arguments for updating.

        .. note::
            The method :meth:`update` is similar to \
            `dict.update <https://docs.python.org/3/library/stdtypes.html#dict.update>`_.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.update({'a': 10, 'f': 'sdkj'})  # with dict
            >>> t
            <TreeValue 0x7fa31f5ba048>
            ├── 'a' --> 10
            ├── 'b' --> 3
            ├── 'c' --> '233'
            └── 'f' --> 'sdkj'
            >>> t.update(a=100, ft='fffff')  # with key-word arguments
            >>> t
            <TreeValue 0x7fa31f5ba048>
            ├── 'a' --> 100
            ├── 'b' --> 3
            ├── 'c' --> '233'
            ├── 'f' --> 'sdkj'
            └── 'ft' --> 'fffff'
            >>> t.update(TreeValue({'f': {'x': 1}, 'b': 40}))  # with TreeValue
            >>> t
            <TreeValue 0x7fa31f5ba048>
            ├── 'a' --> 100
            ├── 'b' --> 40
            ├── 'c' --> '233'
            ├── 'f' --> <TreeValue 0x7fa31f5ba278>
            │   └── 'x' --> 1
            └── 'ft' --> 'fffff'
        """
        self._update(__update_dict, kwargs)

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
    def __getattribute__(self, str item):
        """
        Get item from this tree value.

        :param item: Name of attribute.
        :return: Target attribute value; if ``item`` is exist in :meth:`keys`, return its value.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.a
            1
            >>> t.b
            2
            >>> t.x
            <TreeValue 0x7fd2553e3fd0>
            ├── 'c' --> 3
            └── 'd' --> 4
            >>> t.x.c
            3
            >>> t.keys  # this is a method
            <bound method TreeValue.keys of <TreeValue 0x7fd2553f00b8>>
            >>> t.ff  # this key is not exist
            AttributeError: Attribute 'ff' not found.
        """

        # the order of the attributes' getting is altered
        # original order: __dict__, self._st, self._attr_extern
        # new order: self._st, __dict__, self._attr_extern
        # this may cause problem when pickle.loads, so __getnewargs_ex__ and __cinit__ is necessary
        if self._st.contains(item):
            return self._unraw(self._st.get(item), item)
        else:
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                return self._attr_extern(item)

    @cython.binding(True)
    def __setattr__(self, str key, object value):
        """
        Set sub node to this tree value.

        :param key: Name of the attribute.
        :param value: Sub value.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t.a = 3  # set a value
            >>> t
            <TreeValue 0x7fd2553f0048>
            ├── 'a' --> 3
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fd2553f0080>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> t.b = {'x': 1, 'y': 2}  # set a dict
            >>> t
            <TreeValue 0x7fd2553f0048>
            ├── 'a' --> 3
            ├── 'b' --> {'x': 1, 'y': 2}
            └── 'x' --> <TreeValue 0x7fd2553f0080>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> t.b = TreeValue({'x': 1, 'y': 2})  # set a tree
            >>> t
            <TreeValue 0x7fd2553f0048>
            ├── 'a' --> 3
            ├── 'b' --> <TreeValue 0x7fd2553e3fd0>
            │   ├── 'x' --> 1
            │   └── 'y' --> 2
            └── 'x' --> <TreeValue 0x7fd2553f0080>
                ├── 'c' --> 3
                └── 'd' --> 4
        """
        self._st.set(key, self._raw(value))

    @cython.binding(True)
    def __delattr__(self, str item):
        """
        Delete attribute from tree value.

        :param item: Name of the attribute.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t.a
            >>> t
            <TreeValue 0x7fd2251ae320>
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fd2553f00b8>
                ├── 'c' --> 3
                └── 'd' --> 4
            >>> del t.x.c
            >>> t
            <TreeValue 0x7fd2251ae320>
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7fd2553f00b8>
                └── 'd' --> 4
        """
        try:
            self._st.del_(item)
        except KeyError:
            raise AttributeError(f"Unable to delete attribute {item!r}.")

    @cython.binding(True)
    cpdef _getitem_extern(self, object key):
        r"""
        External protected function for support the :meth:`__getitem__` operation. \
        Default behaviour is raising a `KeyError`.

        :param key: Item object.
        :return: Anything you like, this depends on your implements. 
        :raise KeyError: If it is not able to validly return anything, just raise an ``KeyError`` here.
        """
        raise KeyError(key)

    @cython.binding(True)
    def __getitem__(self, object key):
        """
        Get item from this tree value.

        :param key: Item object.
        :return: Target object value.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t['a']
            1
            >>> t['b']
            2
            >>> t['x']['c']
            3
        """
        if isinstance(key, str):
            return self._unraw(self._st.get(key), key)
        else:
            return self._getitem_extern(_item_unwrap(key))

    @cython.binding(True)
    cpdef _setitem_extern(self, object key, object value):
        r"""
        External function for supporting :meth:`__setitem__` operation.
        
        :param key: Key object.
        :param value: Value object.
        :raise NotImplementedError: When not implemented, raise ``NotImplementedError``. 
        """
        raise NotImplementedError

    @cython.binding(True)
    def __setitem__(self, object key, object value):
        """
        Set item to current :class:`TreeValue` object.

        :param key: Key object.
        :param value: Value object.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t['a'] = 11
            >>> t['x']['c'] = 30
            >>> t
            <TreeValue 0x7f11704c5358>
            ├── 'a' --> 11
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7f11704c52e8>
                ├── 'c' --> 30
                └── 'd' --> 4
        """
        if isinstance(key, str):
            self._st.set(key, self._raw(value))
        else:
            self._setitem_extern(_item_unwrap(key), value)

    @cython.binding(True)
    cpdef _delitem_extern(self, object key):
        r"""
        External function for supporting :meth:`__delitem__` operation.

        :param key: Key object.
        :raise KeyError: Raise ``KeyError`` in default case.
        """
        raise KeyError(key)

    @cython.binding(True)
    def __delitem__(self, object key):
        """
        Delete item from current :class:`TreeValue`.

        :param key: Key object.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> del t['a']
            >>> del t['x']['c']
            >>> t
            <TreeValue 0x7f11704c53c8>
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7f11704c5438>
                └── 'd' --> 4
        """
        if isinstance(key, str):
            self._st.del_(key)
        else:
            self._delitem_extern(_item_unwrap(key))

    @cython.binding(True)
    def __contains__(self, str key):
        """
        Check if attribute is in this tree value.

        :param key: Key to check.
        :return: ``key`` is existed or not in this tree value.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> 'a' in t  # True
            >>> 'b' in t  # True
            >>> 'c' in t  # False
        """
        return self._st.contains(key)

    @cython.binding(True)
    def __iter__(self):
        """
        Get iterator of this tree value.

        :return: An iterator for the keys.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': 3})
            >>> for key in t:
            ...     print(key)
            a
            b
            x

        .. note::
            The method :meth:`__iter__`'s bahaviour should be similar to \
            `dict.__iter__ <https://docs.python.org/3/library/stdtypes.html#dict.update>`_.
        """
        yield from self._st.iter_keys()

    @cython.binding(True)
    def __reversed__(self):
        """
        Get the reversed iterator of tree value.

        :return: A reversed iterator for the keys.

        Examples:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': 3})
            >>> for key in reversed(t):
            ...     print(key)
            x
            b
            a

        .. note::
            Only available in python 3.8 or higher version.
        """
        if _reversible:
            return self._st.iter_rev_keys()
        else:
            raise TypeError(f'{self._type.__name__!r} object is not reversible')

    @cython.binding(True)
    def __len__(self):
        """
        Get count of the keys.

        :return: Count of the keys.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> len(t)    # 3
            >>> len(t.x)  # 2
        """
        return self._st.size()

    @cython.binding(True)
    def __bool__(self):
        """
        Check if the tree value is not empty.

        :return: Not empty or do.

        Example:
            >>> from treevalue import TreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'e': {}})
            >>> not not t    # True
            >>> not not t.x  # True
            >>> not not t.e  # False
        """
        return not self._st.empty()

    @cython.binding(True)
    def __repr__(self):
        """
        Get representation format of tree value.

        :return: Represenation string.

        Example:
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t
            <TreeValue 0x7f672fc53320>
            ├── 'a' --> 1
            ├── 'b' --> 2
            └── 'x' --> <TreeValue 0x7f672fc53390>
                ├── 'c' --> 3
                └── 'd' --> 4
        """
        return format_tree(
            _build_tree(self._detach(), self._type, '', {}, ()),
            itemgetter(0), itemgetter(1),
        )

    @cython.binding(True)
    def __hash__(self):
        """
        Hash value of current object.

        :return: Hash value of current object.

        .. note::
            If the structure and hash values of two tree values are exactly the same, their hash value \
            is guaranteed to be the same.
        """
        return hash(self._st)

    @cython.binding(True)
    def __eq__(self, object other):
        """
        Check the equality of two tree values.

        :param other: Another tree value object.
        :return: Equal or not.

        Example:
            >>> from treevalue import TreeValue, clone, FastTreeValue
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            >>> t == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})      # True
            >>> t == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 5}})      # False
            >>> t == FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})  # False (type not match)
        """
        if self is other:
            return True
        elif type(other) == self._type:
            return self._st == other._detach()
        else:
            return False

    @cython.binding(True)
    def __setstate__(self, tuple state):
        """
        Deserialize operation, can support `pickle.loads`.

        :param state: :class:`treevalue.tree.common.TreeStorage` object, \
            which should be used when deserialization.

        Examples:
            >>> import pickle
            >>> from treevalue import TreeValue
            >>>
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
            >>> bin_ = pickle.dumps(t)  # dump it to binary
            >>> pickle.loads(bin_)      #  TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
        """
        self._st, self.constraint = state

    @cython.binding(True)
    def __getstate__(self):
        """
        Serialize operation, can support `pickle.dumps`.

        :return: A :class:`treevalue.tree.common.TreeStorage` object, used for serialization.

        Examples:
            >>> import pickle
            >>> from treevalue import TreeValue
            >>>
            >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
            >>> bin_ = pickle.dumps(t)  # dump it to binary
            >>> pickle.loads(bin_)      #  TreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
        """
        return self._st, self.constraint

    @cython.binding(True)
    cpdef treevalue_keys keys(self):
        """
        Get keys of this treevalue object, like the :class:`dict`.

        :return: A mapping object for tree value's keys. 

        Examples:
            >>> from treevalue import TreeValue
            >>> 
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.keys()
            treevalue_keys(['a', 'b', 'c'])
            >>> len(t.keys())
            3
            >>> list(t.keys())
            ['a', 'b', 'c']
            >>> list(reversed(t.keys()))  # only available in python3.8+
            ['c', 'b', 'a']
            >>> 'a' in t.keys()
            True
            >>> 'f' in t.keys()
            False

        .. note::
            :func:`reversed` is only available in python 3.8 or higher versions.
        """
        return treevalue_keys(self, self._st)

    @cython.binding(True)
    cpdef treevalue_values values(self):
        """
        Get value of this treevalue object, like the :class:`dict`.

        :return: A mapping object for tree value's values.

        Examples:
            >>> from treevalue import TreeValue
            >>> 
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.values()
            treevalue_values([1, 3, '233'])
            >>> len(t.values())
            3
            >>> list(t.values())
            [1, 3, '233']
            >>> list(reversed(t.values()))  # only supported on python3.8+
            ['233', 3, 1]
            >>> 1 in t.values()
            True
            >>> 'fff' in t.values()
            False

        .. note::
            :func:`reversed` is only available in python 3.8 or higher versions.
        """
        return treevalue_values(self, self._st)

    @cython.binding(True)
    cpdef treevalue_items items(self):
        """
        Get pairs of keys and values of this treevalue object, like the :class:`items`.

        :return: A mapping object for tree value's items.

        Examples:
            >>> from treevalue import TreeValue
            >>> 
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.items()
            treevalue_items([('a', 1), ('b', 3), ('c', '233')])
            >>> len(t.items())
            3
            >>> list(t.items())
            [('a', 1), ('b', 3), ('c', '233')]
            >>> list(reversed(t.items()))  # only supported on python3.8+
            [('c', '233'), ('b', 3), ('a', 1)]
            >>> ('a', 1) in t.items()
            True
            >>> ('c', '234') in t.values()
            False

        .. note::
            :func:`reversed` is only available in python 3.8 or higher versions.
        """
        return treevalue_items(self, self._st)

    @cython.binding(True)
    cpdef void validate(self) except*:
        cdef bool retval
        cdef tuple retpath
        cdef Constraint retcons
        cdef Exception reterr

        if __debug__:
            retval, retpath, retcons, reterr = self.constraint.check(self)
            if not retval:
                raise ValidationError(self, reterr, retpath, retcons)

    @cython.binding(True)
    def with_constraints(self, object constraint, bool clear=False):
        if clear:
            return self._type(self._st, to_constraint(constraint))
        else:
            return self._type(self._st, to_constraint([constraint, self.constraint]))

cdef str _prefix_fix(object text, object prefix):
    cdef list lines = []
    cdef int i
    cdef str line
    cdef str white = ' ' * len(prefix)
    for i, line in enumerate(text.splitlines()):
        lines.append((prefix if i == 0 else white) + line)

    return os.linesep.join(lines)

cdef inline str _title_repr(TreeStorage st, object type_):
    return f'<{type_.__name__} {hex(id(st))}>'

cdef object _build_tree(TreeStorage st, object type_, str prefix, dict id_pool, tuple path):
    cdef object nid = id(st)
    cdef str self_repr = _title_repr(st, type_)
    cdef list children = []

    cdef str k, _t_prefix
    cdef object v, nv
    cdef dict data
    cdef tuple curpath
    if nid in id_pool:
        self_repr = os.linesep.join([
            self_repr, f'(The same address as {".".join(("<root>", *id_pool[nid]))})'])
    else:
        id_pool[nid] = path
        data = st.detach()
        for k, v in sorted(data.items()):
            v = _c_undelay_data(data, k, v)
            curpath = path + (k,)
            _t_prefix = f'{repr(k)} --> '
            if isinstance(v, TreeStorage):
                children.append(_build_tree(v, type_, _t_prefix, id_pool, curpath))
            else:
                children.append((_prefix_fix(repr(v), _t_prefix), []))

    self_repr = _prefix_fix(self_repr, prefix)
    return self_repr, children

# noinspection PyPep8Naming
cdef class treevalue_keys(_CObject, Sized, Container, Reversible):
    def __cinit__(self, TreeValue tv, TreeStorage storage):
        self._st = storage
        self._type = type(tv)

    def __len__(self):
        return self._st.size()

    def __contains__(self, item):
        return self._st.contains(item)

    def _iter(self):
        for k in self._st.iter_keys():
            yield k

    def __iter__(self):
        return self._iter()

    def _rev_iter(self):
        for k in self._st.iter_rev_keys():
            yield k

    def __reversed__(self):
        if _reversible:
            return self._rev_iter()
        else:
            raise TypeError(f'{type(self).__name__!r} object is not reversible')

    def __repr__(self):
        return f'{type(self).__name__}({list(self)!r})'

# noinspection PyPep8Naming
cdef class treevalue_values(_CObject, Sized, Container, Reversible):
    def __cinit__(self, TreeValue tv, TreeStorage storage):
        self._st = storage
        self._type = type(tv)
        self._constraint = tv.constraint
        self._child_constraints = {}

    def __len__(self):
        return self._st.size()

    def __contains__(self, item):
        for v in self:
            if item == v:
                return True

        return False

    cdef inline _SimplifiedConstraintProxy _transact(self, str key):
        cdef _SimplifiedConstraintProxy cons
        if key in self._child_constraints:
            return self._child_constraints[key]
        else:
            cons = _SimplifiedConstraintProxy(transact(self._constraint, key))
            self._child_constraints[key] = cons
            return cons

    def _iter(self):
        for k, v in self._st.iter_items():
            if isinstance(v, TreeStorage):
                yield self._type(v, self._transact(k))
            else:
                yield v

    def __iter__(self):
        return self._iter()

    def _rev_iter(self):
        for k, v in self._st.iter_rev_items():
            if isinstance(v, TreeStorage):
                yield self._type(v, self._transact(k))
            else:
                yield v

    def __reversed__(self):
        if _reversible:
            return self._rev_iter()
        else:
            raise TypeError(f'{type(self).__name__!r} object is not reversible')

    def __repr__(self):
        return f'{type(self).__name__}({list(self)!r})'

# noinspection PyPep8Naming
cdef class treevalue_items(_CObject, Sized, Container, Reversible):
    def __cinit__(self, TreeValue tv, TreeStorage storage):
        self._st = storage
        self._type = type(tv)
        self._constraint = tv.constraint
        self._child_constraints = {}

    def __len__(self):
        return self._st.size()

    def __contains__(self, item):
        for k, v in self:
            if item == (k, v):
                return True

        return False

    cdef inline _SimplifiedConstraintProxy _transact(self, str key):
        cdef _SimplifiedConstraintProxy cons
        if key in self._child_constraints:
            return self._child_constraints[key]
        else:
            cons = _SimplifiedConstraintProxy(transact(self._constraint, key))
            self._child_constraints[key] = cons
            return cons

    def _iter(self):
        for k, v in self._st.iter_items():
            if isinstance(v, TreeStorage):
                yield k, self._type(v, self._transact(k))
            else:
                yield k, v

    def __iter__(self):
        return self._iter()

    def _rev_iter(self):
        for k, v in self._st.iter_rev_items():
            if isinstance(v, TreeStorage):
                yield k, self._type(v, self._transact(k))
            else:
                yield k, v

    def __reversed__(self):
        if _reversible:
            return self._rev_iter()
        else:
            raise TypeError(f'{type(self).__name__!r} object is not reversible')

    def __repr__(self):
        return f'{type(self).__name__}({list(self)!r})'

cdef class DetachedDelayedProxy(DelayedProxy):
    def __init__(self, DelayedProxy proxy):
        self.proxy = proxy
        self.calculated = False
        self.val = None

    cpdef object value(self):
        if not self.calculated:
            self.val = undelay(self.proxy, False)
            self.calculated = True

        return self.val

    cpdef object fvalue(self):
        cdef object v = self.value()
        if isinstance(v, TreeValue):
            v = v._detach()
        return v

@cython.binding(True)
def delayed(func, *args, **kwargs):
    r"""
    Overview:
        Use delayed function in treevalue.
        The given ``func`` will not be called until its value is accessed, and \
        it will be only called once, after that the delayed node will be replaced by the actual value.

    :param func: Delayed function.
    :param args: Positional arguments.
    :param kwargs: Key-word arguments.

    Examples:
        >>> from treevalue import TreeValue, delayed
        >>> def f(x):
        ...     print('f is called, x is', x)
        ...     return x ** x
        ...
        >>> t = TreeValue({'a': delayed(f, 2), 'x': delayed(f, 3)})
        >>> t.a
        f is called, x is 2
        4
        >>> t.x
        f is called, x is 3
        27
        >>> t.a
        4
        >>> t.x
        27
        >>> t = TreeValue({'a': delayed(f, 2), 'x': delayed(f, 3)})
        >>> print(t)
        f is called, x is 2
        f is called, x is 3
        <TreeValue 0x7f672fc53550>
        ├── 'a' --> 4
        └── 'x' --> 27
        >>> print(t)
        <TreeValue 0x7f672fc53550>
        ├── 'a' --> 4
        └── 'x' --> 27
    """
    return DetachedDelayedProxy(_c_delayed_partial(func, args, kwargs))
