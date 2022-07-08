# distutils:language=c++
# cython:language_level=3

from copy import deepcopy
cimport cython

from libcpp cimport bool

from .base cimport raw, unraw
from .delay cimport undelay

cdef inline object _keep_object(object obj):
    return obj

@cython.final
cdef class TreeStorage:
    def __cinit__(self, dict map_):
        self.map = map_

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return ({},), {}

    cpdef public inline void set(self, str key, object value) except *:
        """
        Set value of given ``key`` in this storage object.

        :param key: Key of the target item, should be a string.
        :param value: Value of the target item, should be a native object, raw wrapped object or \\
            a delayed object.
        """
        self.map[key] = unraw(value)

    cpdef public inline object setdefault(self, str key, object default):
        """
        Set value of given ``key`` if it is not exist yet.

        :param key: Key of the target item, should be a string.
        :param default: Default value of the target item, similar to ``value`` in method :meth:`set`.
        :return: Value of the actual-exist item.
        """
        cdef object v, df
        try:
            v = self.map[key]
            return _c_undelay_data(self.map, key, v)
        except KeyError:
            df = unraw(default)
            self.map[key] = df
            return _c_undelay_data(self.map, key, df)

    # get and get_or_default is designed separately due to the consideration of performance
    cpdef public inline object get(self, str key):
        """
        Get value of the given ``key``.

        :param key: Key of the item.
        :return: Value of the item.
        :raise KeyError: When ``key`` is not exist, raise ``KeyError``.
        """
        cdef object v
        v = self.map[key]
        return _c_undelay_data(self.map, key, v)

    cpdef public inline object get_or_default(self, str key, object default):
        """
        Get value of the given ``key``, return ``default`` when not exist.

        :param key: Key of the item.
        :param default: Default value of the item.
        :return: Value of the item if ``key`` is exist, otherwise return ``default``.
        """
        cdef object v
        v = self.map.get(key, default)
        return _c_undelay_check_data(self.map, key, v)

    # pop and pop_or_default is designed separately due to the consideration of performance
    cpdef public inline object pop(self, str key):
        """
        Pop the item with the given ``key``, and return its value.
        After :meth:`pop` method, the ``key`` will be no longer in current storage object.

        :param key: Key of the item.
        :return: Value of the item.
        :raise KeyError: When ``key`` is not exist, raise ``KeyError``.
        """
        return undelay(self.map.pop(key))

    cpdef public inline object pop_or_default(self, str key, object default):
        """
        Pop the item with the given ``key``, return its value when exist, otherwise return ``default``.

        :param key: Key of the item.
        :param default: Default value of the item.
        :return: Value of the item if ``key`` is exist, otherwise return ``default``.
        """
        return undelay(self.map.pop(key, default))

    cpdef public inline tuple popitem(self):
        """
        Pop one item from current storage.

        :return: Tuple of the key and its value.
        :raise KeyError: When current storage is empty, raise ``KeyError``.
        """
        cdef str k
        cdef object v
        k, v = self.map.popitem()
        return k, undelay(v)

    cpdef public inline void del_(self, str key) except *:
        """
        Delete the item with given ``key``.

        :param key: Key of the item.
        :raise KeyError: When ``key`` is not exist, raise ``KeyError``.
        """
        del self.map[key]

    cpdef public inline void clear(self):
        """
        Clear all the items in current storage.
        """
        self.map.clear()

    cpdef public inline boolean contains(self, str key):
        """
        Return true if ``key`` is exist in current storage, otherwise return false.

        :param key: Key.
        :return: ``key`` is exist or not.
        """
        return key in self.map

    cpdef public inline uint size(self):
        """
        Return the size of the current storage.

        :return: Size of current storage.
        """
        return len(self.map)

    cpdef public inline boolean empty(self):
        """
        Return true if current storage is empty (size is 0), otherwise return false.

        :return: Empty or not.
        """
        return not self.map

    cpdef public dict dump(self):
        return self.deepdumpx(_keep_object)

    cpdef public dict deepdump(self):
        return self.deepdumpx(deepcopy)

    cpdef public dict deepdumpx(self, copy_func):
        return self.jsondumpx(copy_func, True, False)

    cpdef public dict jsondumpx(self, copy_func, bool need_raw, bool allow_delayed):
        cdef dict result = {}
        cdef str k
        cdef object v, obj, nv
        for k, v in self.map.items():
            if not allow_delayed:
                v = _c_undelay_data(self.map, k, v)

            if isinstance(v, TreeStorage):
                result[k] = v.jsondumpx(copy_func, need_raw, allow_delayed)
            else:
                obj = copy_func(v) if not allow_delayed else v
                if need_raw:
                    obj = raw(obj)
                result[k] = obj

        return result

    cpdef public TreeStorage copy(self):
        return self.deepcopyx(_keep_object, True)

    cpdef public TreeStorage deepcopy(self):
        return self.deepcopyx(deepcopy, False)

    cpdef public TreeStorage deepcopyx(self, copy_func, bool allow_delayed):
        return create_storage(self.jsondumpx(copy_func, True, allow_delayed))

    cpdef public dict detach(self):
        return self.map

    cpdef public void copy_from(self, TreeStorage ts):
        self.deepcopyx_from(ts, _keep_object, True)

    cpdef public void deepcopy_from(self, TreeStorage ts):
        self.deepcopyx_from(ts, deepcopy, False)

    cpdef public void deepcopyx_from(self, TreeStorage ts, copy_func, bool allow_delayed):
        cdef dict detached = ts.detach()
        cdef set keys = set(self.map.keys()) | set(detached.keys())

        cdef str k
        cdef object v, nv
        cdef TreeStorage newv
        for k in keys:
            if k in detached:
                v = detached[k]
                if not allow_delayed:
                    v = _c_undelay_data(detached, k, v)

                if isinstance(v, TreeStorage):
                    if k in self.map and isinstance(self.map[k], TreeStorage):
                        self.map[k].deepcopyx_from(v, copy_func, allow_delayed)
                    else:
                        newv = TreeStorage({})
                        newv.deepcopyx_from(v, copy_func, allow_delayed)
                        self.map[k] = newv
                else:
                    if not allow_delayed:
                        self.map[k] = copy_func(v)
                    else:
                        self.map[k] = v
            else:
                del self.map[k]

    def __getstate__(self):
        return self.map

    def __setstate__(self, state):
        self.map = state

    def __repr__(self):
        cdef tuple keys = tuple(sorted(self.map.keys()))
        cdef str clsname = self.__class__.__name__
        return f'<{clsname} at {hex(id(self))}, keys: {repr(keys)}>'

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) != type(other):
            return False

        cdef list self_keys = sorted(self.map.keys())
        cdef dict other_map = other.detach()
        cdef list other_keys = sorted(other.detach().keys())

        cdef str key
        cdef object self_v, self_nv
        cdef object other_v, other_nv
        if self_keys == other_keys:
            for key in self_keys:
                self_v = self.map[key]
                self_v = _c_undelay_data(self.map, key, self_v)

                other_v = other_map[key]
                other_v = _c_undelay_data(other_map, key, other_v)

                if self_v != other_v:
                    return False
            return True
        else:
            return False

    def __hash__(self):
        cdef str k
        cdef object v
        cdef list _items = []
        for k, v in sorted(self.iter_items(), key=lambda x: x[0]):
            _items.append((k, v))

        return hash(tuple(_items))

    def iter_keys(self):
        """
        Iterate keys in current storage.

        :return: Iterator of current keys in normal order.
        """
        return self.map.keys()

    def iter_rev_keys(self):
        """
        Reversely iterate keys in current storage.

        :return: Iterator of current keys in reversed order.
        """
        return reversed(self.map.keys())

    def iter_values(self):
        """
        Iterate values in current storage.

        :return: Iterator of current values in normal order.
        """
        cdef str k
        cdef object v, nv
        for k, v in self.map.items():
            yield _c_undelay_data(self.map, k, v)

    def iter_rev_values(self):
        """
        Reversely iterate values in current storage.

        :return: Iterator of current values in reversed order.
        """
        cdef str k
        cdef object v, nv
        for k, v in reversed(self.map.items()):
            yield _c_undelay_data(self.map, k, v)

    def iter_items(self):
        """
        Iterate items in current storage.

        :return: Iterator of current items in normal order.
        """
        cdef str k
        cdef object v, nv
        for k, v in self.map.items():
            yield k, _c_undelay_data(self.map, k, v)

    def iter_rev_items(self):
        """
        Reversely iterate items in current storage.

        :return: Iterator of current items in reversed order.
        """
        cdef str k
        cdef object v, nv
        for k, v in reversed(self.map.items()):
            yield k, _c_undelay_data(self.map, k, v)


cpdef inline object create_storage(dict value):
    cdef dict _map = {}
    cdef str k
    cdef object v
    for k, v in value.items():
        if isinstance(v, dict):
            _map[k] = create_storage(v)
        else:
            _map[k] = unraw(v)

    return TreeStorage(_map)

cdef inline object _c_undelay_data(dict data, object k, object v):
    cdef object nv = undelay(v)
    if nv is not v:
        data[k] = nv
    return nv

cdef inline object _c_undelay_not_none_data(dict data, object k, object v):
    cdef object nv = undelay(v)
    if nv is not v and k is not None:
        data[k] = nv
    return nv

cdef inline object _c_undelay_check_data(dict data, object k, object v):
    cdef object nv = undelay(v)
    if nv is not v and k in data:
        data[k] = nv
    return nv