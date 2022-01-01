# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from libcpp cimport bool

cdef class _SubsideCall:
    cdef object run

cdef object _c_subside_process(tuple value, object it)
cdef tuple _c_subside_build(object value, bool dict_, bool list_, bool tuple_)
cdef void _c_subside_missing()
cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit,
                       object mode, object missing, bool delayed)
cdef object _c_subside_keep_type(object t)
cpdef object subside(object value, bool dict_= *, bool list_= *, bool tuple_= *,
                     object return_type= *, bool inherit= *, object mode= *, object missing= *, bool delayed= *)

cdef object _c_rise_tree_builder(tuple p, object it)
cdef tuple _c_rise_tree_process(object t)
cdef object _c_rise_struct_builder(tuple p, object it)
cdef tuple _c_rise_struct_process(list objs, object template)
cdef object _c_rise_keep_type(object t)
cdef object _c_rise(object tree, bool dict_, bool list_, bool tuple_, object template_)
