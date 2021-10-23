# distutils:language=c++
# cython:language_level=3

from ..common.storage cimport TreeStorage

cdef class TreeValue:
    cdef TreeStorage _st
    cdef type _type

    cpdef TreeStorage _detach(self)
    cdef object _unraw(self, object obj)
    cdef object _raw(self, object obj)
    cpdef _attr_extern(self, str key)

cdef str _prefix_fix(object text, object prefix)
cdef object _build_tree(TreeStorage st, object type_, str prefix, dict id_pool, tuple path)
