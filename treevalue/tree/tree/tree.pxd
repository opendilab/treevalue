# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

from ..common.delay cimport DelayedProxy
from ..common.storage cimport TreeStorage

cdef class _CObject:
    pass

cdef class TreeValue:
    cdef readonly TreeStorage _st
    cdef readonly type _type

    cpdef TreeStorage _detach(self)
    cdef object _unraw(self, object obj)
    cdef object _raw(self, object obj)
    cpdef _attr_extern(self, str key)
    cpdef _getitem_extern(self, object key)
    cpdef _setitem_extern(self, object key, object value)
    cpdef _delitem_extern(self, object key)
    cpdef get(self, str key, object default= *)
    cpdef pop(self, str key, object default= *)

    cpdef treevalue_keys keys(self)
    cpdef treevalue_values values(self)
    cpdef treevalue_items items(self)

cdef str _prefix_fix(object text, object prefix)
cdef str _title_repr(TreeStorage st, object type_)
cdef object _build_tree(TreeStorage st, object type_, str prefix, dict id_pool, tuple path)

# noinspection PyPep8Naming
cdef class treevalue_keys(_CObject):
    cdef readonly TreeStorage _st
    cdef readonly type _type

# noinspection PyPep8Naming
cdef class treevalue_values(_CObject):
    cdef readonly TreeStorage _st
    cdef readonly type _type

# noinspection PyPep8Naming
cdef class treevalue_items(_CObject):
    cdef readonly TreeStorage _st
    cdef readonly type _type

cdef class DetachedDelayedProxy(DelayedProxy):
    cdef DelayedProxy proxy
    cdef readonly bool calculated
    cdef object val

    cpdef object value(self)
    cpdef object fvalue(self)
