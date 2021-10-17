# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef class _ValuePathFuncWrapper:
    cdef readonly object func
    cdef int index

cdef TreeStorage _c_mapping(TreeStorage st, object func, tuple path)
cpdef TreeValue mapping(TreeValue t, object func)
cdef TreeStorage _c_filter_(TreeStorage st, object func, tuple path, bool remove_empty)
cpdef TreeValue filter_(TreeValue t, object func, bool remove_empty= *)
cdef object _c_mask(TreeStorage st, object sm, tuple path, bool remove_empty)
cpdef TreeValue mask(TreeValue tree, object mask_, bool remove_empty=*)
