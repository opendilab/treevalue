# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

cdef class DelayedProxy:
    cpdef object value(self)
    cpdef object fvalue(self)

cdef class DelayedValueProxy(DelayedProxy):
    cdef readonly object func
    cdef readonly bool calculated
    cdef object val

    cpdef object value(self)

cdef class DelayedFuncProxy(DelayedProxy):
    cdef readonly object func
    cdef readonly tuple args
    cdef readonly dict kwargs
    cdef readonly bool calculated
    cdef object val

    cpdef object value(self)

cdef DelayedProxy _c_delayed_partial(func, args, kwargs)
cpdef object undelay(object p, bool is_final= *)
