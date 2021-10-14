# distutils:language=c++
# cython:language_level=3

from ..common.storage cimport TreeStorage

cpdef TreeStorage get_data_property(t)

cdef class TreeValue:
    cdef TreeStorage _st
    cdef type _type

    cpdef TreeStorage _detach(self)
    cdef object _unraw(self, object obj)
    cdef object _raw(self, object obj)
    cpdef _attr_extern(self, str key)
    cpdef str _repr(self)
