# distutils:language=c++
# cython:language_level=3

import os
from collections.abc import Sized, Container, Reversible, Mapping
from operator import itemgetter

import cython
from hbutils.design import SingletonMark

from ..common.delay cimport undelay, _c_delayed_partial, DelayedProxy
from ..common.storage cimport TreeStorage, create_storage, _c_undelay_data
from ...utils import format_tree

cdef class _CObject:
    pass

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

cdef class TreeValue:
    r"""
    Overview:
        Base framework of tree value. \
        And if the fast functions and operators are what you need, \
        please use `FastTreeValue` in `treevalue.tree.general`. \
        The `TreeValue` class is a light-weight framework just for DIY.
    """

    def __cinit__(self, object data):
        self._st = _DEFAULT_STORAGE
        self._type = type(self)

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
    cpdef get(self, str key, object default=None):
        r"""
        Overview:
            Get item from the tree node.

        :param key: Item's name.
        :param default: Default value when this item is not found, default is ``None``.
        :return: Item's value.

        .. note::
            The method :meth:`get` will never raise ``KeyError``, like the behaviour in \
            `dict.get <https://docs.python.org/3/library/stdtypes.html#dict.get>`_.
        """
        return self._unraw(self._st.get_or_default(key, default))

    @cython.binding(True)
    cpdef pop(self, str key, object default=_GET_NO_DEFAULT):
        """
        Overview:
            Pop item from the tree node.

        :param key: Item's name.
        :param default: Default value when this item is not found, default is ``_GET_NO_DEFAULT`` which means \
            just raise ``KeyError`` when not found.
        :return: Item's value.

        .. note::
            The method :meth:`pop` will raise ``KeyError`` when ``key`` is not found, like the behaviour in \
            `dict.pop <https://docs.python.org/3/library/stdtypes.html#dict.pop>`_.
        """
        cdef object value
        if default is _GET_NO_DEFAULT:
            value = self._st.pop(key)
        else:
            value = self._st.pop_or_default(key, default)

        return self._unraw(value)

    @cython.binding(True)
    cpdef popitem(self):
        """
        Overview:
            Pop item (with a key and its value) from the tree node.

        :return: Popped item.
        :raise KeyError: When current treevalue is empty.

        .. note::
            The method :meth:`popitem` will raise ``KeyError`` when empty, like the behaviour in \
            `dict.popitem <https://docs.python.org/3/library/stdtypes.html#dict.popitem>`_.
        """
        cdef str k
        cdef object v
        try:
            k, v = self._st.popitem()
            return k, self._unraw(v)
        except KeyError:
            raise KeyError(f'popitem(): {self._type.__name__} is empty.')

    @cython.binding(True)
    cpdef void clear(self):
        """
        Overview:
            Clear all the items in this treevalue object.
        """
        self._st.clear()

    cdef void _update(self, object d, dict kwargs) except *:
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

        Examples::
            >>> from treevalue import TreeValue
            >>>
            >>> t = TreeValue({'a': 1, 'b': 3, 'c': '233'})
            >>> t.update({'a': 10, 'f': 'sdkj'})  # with dict
            >>> t
            <TreeValue 0x7fa31f5ba048>
            ├── 'a' --> 10
            ├── 'b' --> 3
            ├── 'c' --> '233'
            └── 'f' --> 'sdkj'
            >>>
            >>> t.update(a=100, ft='fffff')  # with key-word arguments
            >>> t
            <TreeValue 0x7fa31f5ba048>
            ├── 'a' --> 100
            ├── 'b' --> 3
            ├── 'c' --> '233'
            ├── 'f' --> 'sdkj'
            └── 'ft' --> 'fffff'
            >>>
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

        # original order: __dict__, self._st, self._attr_extern
        # new order: self._st, __dict__, self._attr_extern
        # this may cause problem when pickle.loads, so __getnewargs_ex__ and __cinit__ is necessary
        if self._st.contains(item):
            return self._unraw(self._st.get(item))
        else:
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
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
    cpdef _getitem_extern(self, object key):
        r"""
        Overview:
            External protected function for support the getitem operation. \
            Default is raise a `KeyError`.

        Arguments:
            - key (:obj:`object`): Item object.

        Returns:
            - return (:obj:): Anything you like, \
                and if it is not able to validly return anything, \
                just raise an ``KeyError`` here.
        """
        raise KeyError(f'Key {repr(key)} not found.')

    @cython.binding(True)
    def __getitem__(self, object key):
        """
        Overview:
            Get item from this tree value.

        Arguments:
            - key (:obj:`str`): Item object.

        Returns:
            - value (:obj:): Target object value.

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
            return self._unraw(self._st.get(key))
        else:
            return self._getitem_extern(_item_unwrap(key))

    @cython.binding(True)
    cpdef _setitem_extern(self, object key, object value):
        r"""
        Overview:
            External function for supporting ``__setitem__`` operation.
        
        Arguments:
            - key (:obj:`object`): Key object.
            - value (:obj:`object`): Value object.
        
        Raises:
            - NotImplementError: Just raise this when not implemented.
        """
        raise NotImplementedError

    @cython.binding(True)
    def __setitem__(self, object key, object value):
        """
        Overview:
            Set item to current :class:`TreeValue` object.

        Arguments:
            - key (:obj:`object`): Key object.
            - value (:obj:`object`): Value object.

        Examples::
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
        Overview:
            External function for supporting ``__delitem__`` operation.
        
        Arguments:
            - key (:obj:`object`): Key object.
        
        Raises:
            - KeyError: Just raise this in default case.
        """
        raise KeyError(f'Key {repr(key)} not found.')

    @cython.binding(True)
    def __delitem__(self, object key):
        """
        Overview:
            Delete item from current :class:`TreeValue`.

        Arguments:
            - key (:obj:`object`): Key object.

        Examples::
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
        for k, v in self._st.iter_items():
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
    def __repr__(self):
        """
        Overview:
            Get representation format of tree value.

        Returns:
            - repr (:obj:`str`): Representation string.

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

    @cython.binding(True)
    cpdef treevalue_keys keys(self):
        """
        Overview:
            Get keys of this treevalue object, like the :class:`dict`.

        Returns:
            - keys: A generator of all the keys.

        Examples::
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
        return treevalue_keys(self._st, self._type)

    @cython.binding(True)
    cpdef treevalue_values values(self):
        """
        Overview:
            Get value of this treevalue object, like the :class:`dict`.

        Returns:
            - values: A generator of all the values

        Examples::
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
        return treevalue_values(self._st, self._type)

    @cython.binding(True)
    cpdef treevalue_items items(self):
        """
        Overview:
            Get pairs of keys and values of this treevalue object, like the :class:`items`.

        Returns:
            - items: A generator of pairs of keys and values.

        Examples::
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
        return treevalue_items(self._st, self._type)

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

try:
    reversed({'a': 1}.keys())
except TypeError:
    _reversible = False
else:
    _reversible = True

# noinspection PyPep8Naming
cdef class treevalue_keys(_CObject, Sized, Container, Reversible):
    def __cinit__(self, TreeStorage storage, type _type):
        self._st = storage
        self._type = _type

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
    def __cinit__(self, TreeStorage storage, type _type):
        self._st = storage
        self._type = _type

    def __len__(self):
        return self._st.size()

    def __contains__(self, item):
        for v in self:
            if item == v:
                return True

        return False

    def _iter(self):
        for v in self._st.iter_values():
            if isinstance(v, TreeStorage):
                yield self._type(v)
            else:
                yield v

    def __iter__(self):
        return self._iter()

    def _rev_iter(self):
        for v in self._st.iter_rev_values():
            if isinstance(v, TreeStorage):
                yield self._type(v)
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
    def __cinit__(self, TreeStorage storage, type _type):
        self._st = storage
        self._type = _type

    def __len__(self):
        return self._st.size()

    def __contains__(self, item):
        for k, v in self:
            if item == (k, v):
                return True

        return False

    def _iter(self):
        for k, v in self._st.iter_items():
            if isinstance(v, TreeStorage):
                yield k, self._type(v)
            else:
                yield k, v

    def __iter__(self):
        return self._iter()

    def _rev_iter(self):
        for k, v in self._st.iter_rev_items():
            if isinstance(v, TreeStorage):
                yield k, self._type(v)
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

    Arguments:
        - func: Delayed function.
        - args: Positional arguments.
        - kwargs: Key-word arguments.

    Examples::
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
