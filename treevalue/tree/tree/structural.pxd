# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from libcpp cimport bool

# subside - common value
cdef class _SubsideValue:
    cpdef int size(self)

# subside - dict
cdef class _SubsideDict:
    cdef int count
    cdef list items
    cdef type type_
    cpdef int size(self)

# subside - list, tuple
cdef class _SubsideArray:
    cdef int count
    cdef list items
    cdef type type_
    cpdef int size(self)

cdef tuple _c_subside_build(object value, bool dict_, bool list_, bool tuple_)
cdef void _c_subside_missing()
cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit)
cdef object _c_subside_keep_type(object t)
cpdef object subside(object value, bool dict_= *, bool list_= *, bool tuple_= *,
                     object return_type= *, bool inherit= *)
