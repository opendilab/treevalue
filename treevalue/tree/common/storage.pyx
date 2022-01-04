# distutils:language=c++
# cython:language_level=3

from copy import deepcopy

from libc.string cimport strlen
from libcpp cimport bool

from .base cimport raw, unraw
from .delay cimport undelay

cdef inline object _keep_object(object obj):
    return obj

cdef inline void _key_validate(const char *key) except *:
    cdef int n = strlen(key)
    if n < 1:
        raise KeyError(f'Key {repr(key)} is too short, minimum length is 1 but {n} found.')
    elif n > 256:
        raise KeyError(f'Key {repr(key)} is too long, maximum length is 256 but {n} found.')

    cdef int i
    for i in range(n):
        if not (b'a' <= key[i] <= b'z' or b'A' <= key[i] <= b'Z' or key[i] == b'_'
                or (i > 0 and b'0' <= key[i] <= b'9')):
            raise KeyError(f'Invalid char {repr(key[i])} detected in position {repr(i)} of key {repr(key)}.')

cdef class TreeStorage:
    def __cinit__(self, dict map_):
        self.map = map_

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return ({},), {}

    cpdef public void set(self, str key, object value) except *:
        _key_validate(key.encode())
        self.map[key] = value

    cpdef public object get(self, str key):
        cdef object v, nv
        try:
            v = self.map[key]
            return _c_undelay_data(self.map, key, v)
        except KeyError:
            raise KeyError(f"Key {repr(key)} not found in this tree.")

    cpdef public object get_or_default(self, str key, object default):
        cdef object v, nv
        v = self.map.get(key, default)
        return _c_undelay_check_data(self.map, key, v)

    cpdef public void del_(self, str key) except *:
        try:
            del self.map[key]
        except KeyError:
            raise KeyError(f"Key {repr(key)} not found in this tree.")

    cpdef public boolean contains(self, str key):
        return key in self.map

    cpdef public uint size(self):
        return len(self.map)

    cpdef public boolean empty(self):
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
        for k, v in sorted(self.items(), key=lambda x: x[0]):
            _items.append((k, v))

        return hash(tuple(_items))

    def keys(self):
        return self.map.keys()

    def values(self):
        cdef str k
        cdef object v, nv
        for k, v in self.map.items():
            yield _c_undelay_data(self.map, k, v)

    def items(self):
        cdef str k
        cdef object v, nv
        for k, v in self.map.items():
            v = _c_undelay_data(self.map, k, v)

            yield k, v

cpdef object create_storage(dict value):
    cdef dict _map = {}
    cdef str k
    cdef object v
    for k, v in value.items():
        _key_validate(k.encode())
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