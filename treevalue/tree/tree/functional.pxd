# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef class _MappingFunc:
    cdef readonly object func
    cdef int index

cdef TreeStorage _c_mapping(TreeStorage st, object func, tuple path)
cpdef TreeValue mapping(TreeValue t, object func)
