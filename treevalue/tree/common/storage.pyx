# distutils:language=c++
# cython:language_level=3

from copy import deepcopy

from libc.string cimport strlen

from .base cimport raw, unraw

cdef inline object _keep_object(object obj):
    return obj

cdef inline void _key_validate(const char*key) except *:
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
        try:
            return self.map[key]
        except KeyError:
            raise KeyError(f"Key {repr(key)} not found in this tree.")

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
        cdef dict result = {}
        cdef str k
        cdef object v
        for k, v in self.map.items():
            if isinstance(v, TreeStorage):
                result[k] = v.deepdumpx(copy_func)
            else:
                result[k] = raw(copy_func(v))

        return result

    cpdef public TreeStorage copy(self):
        return self.deepcopyx(_keep_object)

    cpdef public TreeStorage deepcopy(self):
        return self.deepcopyx(deepcopy)

    cpdef public TreeStorage deepcopyx(self, copy_func):
        cdef type cls = type(self)
        return create_storage(self.deepdumpx(copy_func))

    cpdef public dict detach(self):
        return self.map

    cpdef public void copy_from(self, TreeStorage ts):
        self.deepcopyx_from(ts, _keep_object)

    cpdef public void deepcopy_from(self, TreeStorage ts):
        self.deepcopyx_from(ts, deepcopy)

    cpdef public void deepcopyx_from(self, TreeStorage ts, copy_func):
        cdef dict detached = ts.detach()
        cdef set keys = set(self.map.keys()) | set(detached.keys())

        cdef str k
        cdef object
        cdef TreeStorage newv
        for k in keys:
            if k in detached:
                v = detached[k]
                if isinstance(v, TreeStorage):
                    if k in self.map and isinstance(self.map[k], TreeStorage):
                        self.map[k].copy_from(v)
                    else:
                        newv = TreeStorage({})
                        newv.copy_from(v)
                        self.map[k] = newv
                else:
                    self.map[k] = copy_func(v)
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

    def __eq__(self, TreeStorage other):
        cdef list self_keys = sorted(self.map.keys())
        cdef dict other_map = other.detach()
        cdef list other_keys = sorted(other.detach().keys())

        cdef str key
        if self_keys == other_keys:
            for key in self_keys:
                if not (self.map[key] == other_map[key]):
                    return False
            return True
        else:
            return False

    def keys(self):
        return self.map.keys()

    def values(self):
        return self.map.values()

    def items(self):
        return self.map.items()

def create_storage(dict value):
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
