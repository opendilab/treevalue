# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

cdef class _WrappedConstraintException(Exception):
    pass

cdef class Constraint:
    cpdef void _validate_node(self, object instance) except*
    cpdef void _validate_value(self, object instance) except*
    cpdef object _features(self)
    cpdef bool _contains(self, Constraint other)
    cpdef Constraint _transaction(self, str key)

    cdef bool _feature_match(self, Constraint other)
    cdef bool _contains_check(self, Constraint other)
    cdef tuple _native_validate(self, object instance, type type_, list path)
    cpdef tuple check(self, object instance)
    cpdef bool equiv(self, object other)

cdef Constraint _r_parse_cons(object obj)
cpdef Constraint to_constraint(object obj)

cdef class EmptyConstraint(Constraint):
    pass

cdef class ValueConstraint(Constraint):
    pass

cdef class NodeConstraint(Constraint):
    pass

cdef class TypeConstraint(ValueConstraint):
    cdef readonly type type_

cdef class LeafConstraint(Constraint):
    pass

cpdef LeafConstraint cleaf()

cdef class TreeConstraint(Constraint):
    cdef readonly dict _constraints

cdef Constraint _s_tree_merge(list constraints)
cdef Constraint _s_tree(TreeConstraint constraint)

cdef class CompositeConstraint(Constraint):
    cdef readonly tuple _constraints

cdef void _rec_composite_iter(Constraint constraint, list lst)
cdef list _r_composite_iter(Constraint constraint)

cdef Constraint _s_generic_merge(list constraints)
cdef Constraint _s_composite(CompositeConstraint constraint)

cdef Constraint _s_simplify(Constraint constraint)