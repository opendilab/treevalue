# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

from ..common.delay cimport DelayedProxy
from ..common.storage cimport TreeStorage

cdef class TreeValue:
    cdef readonly TreeStorage _st
    cdef readonly type _type

    cpdef TreeStorage _detach(self)
    cdef object _unraw(self, object obj)
    cdef object _raw(self, object obj)
    cpdef _attr_extern(self, str key)
    cpdef get(self, str key, object default= *)

cdef str _prefix_fix(object text, object prefix)
cdef object _build_tree(TreeStorage st, object type_, str prefix, dict id_pool, tuple path)

cdef class DetachedDelayedProxy(DelayedProxy):
    cdef DelayedProxy proxy
    cdef readonly bool calculated
    cdef object val

    cpdef object value(self)
    cpdef object fvalue(self)