# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from libcpp cimport bool

cdef class _SubsideCall:
    cdef object run

cdef object _c_subside_process(tuple value, object it)
cdef tuple _c_subside_build(object value, bool dict_, bool list_, bool tuple_)
cdef void _c_subside_missing()
cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit)
cdef object _c_subside_keep_type(object t)
cpdef object subside(object value, bool dict_= *, bool list_= *, bool tuple_= *,
                     object return_type= *, bool inherit= *)
