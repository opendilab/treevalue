# distutils:language=c++
# cython:language_level=3

import cython

cdef class RawWrapper:
    @cython.binding(True)
    def __cinit__(self, object v):
        self.val = v

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return (None,), {}

    @cython.binding(True)
    cpdef object value(self):
        return self.val

    def __getstate__(self):
        return self.val

    def __setstate__(self, state):
        self.val = state

@cython.binding(True)
cpdef public object raw(object obj):
    """
    Overview:
        Try wrap the given ``obj`` to raw wrapper.
        
    Arguments:
        - obj (:obj:`object`): The original object. 

    Returns:
        - wrapped (:obj:`object`): Wrapped object, if the type is not \
            necessary to be wrapped, the original object will be returned here.
    """
    if not isinstance(obj, RawWrapper) and isinstance(obj, dict):
        return RawWrapper(obj)
    else:
        return obj

@cython.binding(True)
cpdef public object unraw(object obj):
    if isinstance(obj, RawWrapper):
        return obj.value()
    else:
        return obj
