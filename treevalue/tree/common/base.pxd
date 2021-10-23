# distutils:language=c++
# cython:language_level=3

cdef class RawWrapper:
    cdef readonly object val

    cpdef object value(self)

cpdef public object raw(object obj)
cpdef public object unraw(object wrapped)
