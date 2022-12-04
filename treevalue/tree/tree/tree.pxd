# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

from .constraint cimport Constraint
from ..common.delay cimport DelayedProxy
from ..common.storage cimport TreeStorage

cdef class _CObject:
    pass

cdef class _SimplifiedConstraintProxy:
    cdef readonly Constraint cons

cdef Constraint _c_get_constraint(object cons)

cdef class ValidationError(Exception):
    cdef readonly TreeValue _object
    cdef readonly Exception _error
    cdef readonly tuple _path
    cdef readonly Constraint _cons

cdef class TreeValue:
    cdef readonly TreeStorage _st
    cdef readonly Constraint constraint
    cdef readonly type _type
    cdef readonly dict _child_constraints

    cpdef TreeStorage _detach(self)
    cdef object _unraw(self, object obj, str key)
    cdef object _raw(self, object obj)
    cpdef _attr_extern(self, str key)
    cpdef _getitem_extern(self, object key)
    cpdef _setitem_extern(self, object key, object value)
    cpdef _delitem_extern(self, object key)
    cdef void _update(self, object d, dict kwargs) except*
    cpdef public get(self, str key, object default= *)
    cpdef public pop(self, str key, object default= *)
    cpdef public popitem(self)
    cpdef public void clear(self)
    cpdef public object setdefault(self, str key, object default= *)

    cpdef public treevalue_keys keys(self)
    cpdef public treevalue_values values(self)
    cpdef public treevalue_items items(self)

    cpdef void validate(self) except*

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
    cdef readonly Constraint _constraint
    cdef readonly dict _child_constraints

    cdef _SimplifiedConstraintProxy _transact(self, str key)

# noinspection PyPep8Naming
cdef class treevalue_items(_CObject):
    cdef readonly TreeStorage _st
    cdef readonly type _type
    cdef readonly Constraint _constraint
    cdef readonly dict _child_constraints

    cdef _SimplifiedConstraintProxy _transact(self, str key)

cdef class DetachedDelayedProxy(DelayedProxy):
    cdef DelayedProxy proxy
    cdef readonly bool calculated
    cdef object val

    cpdef object value(self)
    cpdef object fvalue(self)
