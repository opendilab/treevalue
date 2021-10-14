# distutils:language=c++
# cython:language_level=3

cdef class RawWrapper:
    def __cinit__(self, object v):
        self.val = v

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return (None,), {}

    cpdef object value(self):
        return self.val

    def __getstate__(self):
        return self.val

    def __setstate__(self, state):
        self.val = state

cpdef public object raw(object obj):
    if not isinstance(obj, RawWrapper) and isinstance(obj, dict):
        return RawWrapper(obj)
    else:
        return obj

cpdef public object unraw(object obj):
    if isinstance(obj, RawWrapper):
        return obj.value()
    else:
        return obj
