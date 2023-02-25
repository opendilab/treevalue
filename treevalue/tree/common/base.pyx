# distutils:language=c++
# cython:language_level=3

import cython
from libcpp cimport bool

cdef class RawWrapper:
    """
    Wrapper class of the raw value.
    """
    @cython.binding(True)
    def __cinit__(self, object v):
        """
        Overview:
            C-leveled constructor of :class:`RawWrapper`.

        Arguments:
            - v (:obj:`object`): Value to be wrapped.
        """
        self.val = v

    def __getnewargs_ex__(self):  # for __cinit__, when pickle.loads
        return (None,), {}

    @cython.binding(True)
    cpdef object value(self):
        """
        Overview:
            Get wrapped original value.

        Returns:
            - obj: Original value.
        """
        return self.val

    def __getstate__(self):
        return self.val

    def __setstate__(self, state):
        self.val = state

_TYPES_NEED_WRAP = (dict,)
_WRAPPED_KEY = '__treevalue/raw/wrapper'

cdef inline bool _c_is_unsafe_wrapped(object wrapped):
    return isinstance(wrapped, RawWrapper)

cdef inline bool _c_is_safe_wrapped(object wrapped):
    cdef str key
    if isinstance(wrapped, dict) and len(wrapped) == 1:
        key, = wrapped.keys()
        return key == _WRAPPED_KEY
    else:
        return False

@cython.binding(True)
cpdef inline object raw(object obj, object safe=None):
    """
    Overview:
        Try wrap the given ``obj`` to raw wrapper.
        
    Arguments:
        - obj (:obj:`object`): The original object.
        - safe (:obj:`object`): Safe or not. When true, a dict will be used to wrap the value. 

    Returns:
        - wrapped (:obj:`object`): Wrapped object, if the type is not \
            necessary to be wrapped, the original object will be returned here.
    """
    if _c_is_safe_wrapped(obj):
        if safe is not None and not safe:
            return raw(unraw(obj), safe=safe)
        else:
            return obj
    elif _c_is_unsafe_wrapped(obj):
        if safe is not None and safe:
            return raw(unraw(obj), safe=safe)
        else:
            return obj
    else:
        if isinstance(obj, _TYPES_NEED_WRAP):
            if safe:
                return {_WRAPPED_KEY: obj}
            else:
                return RawWrapper(obj)
        else:
            return obj

@cython.binding(True)
cpdef inline object unraw(object wrapped):
    """
    Overview:
        Try unwrap the given ``wrapped`` to original object.

    Arguments:
        - wrapped (:obj:`object`): Wrapped object.

    Returns:
        - obj (:obj:`object`): The original object.
    """
    if _c_is_unsafe_wrapped(wrapped):
        return wrapped.value()
    elif _c_is_safe_wrapped(wrapped):
        return wrapped[_WRAPPED_KEY]
    else:
        return wrapped
