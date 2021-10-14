# distutils:language=c++
# cython:language_level=3

cdef class _RawWrapper:
    cdef public object value

    def __cinit__(self, v):
        self.value = v

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return (None,), {}

    def __getstate__(self):
        return self.value

    def __setstate__(self, state):
        self.value = state

cpdef public inline object raw(object obj):
    if not isinstance(obj, _RawWrapper) and isinstance(obj, dict):
        return _RawWrapper(obj)
    else:
        return obj

cpdef public inline object unraw(object obj):
    if isinstance(obj, _RawWrapper):
        return obj.value
    else:
        return obj
