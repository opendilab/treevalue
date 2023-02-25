# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

cdef class RawWrapper:
    cdef readonly object val

    cpdef object value(self)

cdef bool _c_is_unsafe_wrapped(object wrapped)
cdef bool _c_is_safe_wrapped(object wrapped)
cdef bool _c_is_wrapped(object wrapped)

cpdef public object raw(object obj, object safe= *)
cpdef public object unraw(object wrapped)
