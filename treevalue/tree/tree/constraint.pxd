# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

cdef class _WrappedConstraintException(Exception):
    pass

cdef class BaseConstraint:
    cpdef void _validate_node(self, object instance) except*
    cpdef void _validate_value(self, object instance) except*
    cpdef object _features(self)
    cpdef bool _contains(self, BaseConstraint other)
    cpdef BaseConstraint _transaction(self, str key)

    cdef bool _feature_match(self, BaseConstraint other)
    cdef bool _contains_check(self, BaseConstraint other)
    cdef tuple _native_validate(self, object instance, type type_, list path)
    cpdef tuple check(self, object instance)
    cpdef bool equiv(self, object other)

cdef BaseConstraint _r_parse_cons(object obj)
cpdef BaseConstraint to_constraint(object obj)

cdef class EmptyConstraint(BaseConstraint):
    pass

cdef class ValueConstraint(BaseConstraint):
    pass

cdef class NodeConstraint(BaseConstraint):
    pass

cdef class TypeConstraint(ValueConstraint):
    cdef readonly type type_

cdef class LeafConstraint(BaseConstraint):
    pass

cpdef LeafConstraint cleaf()

cdef class TreeConstraint(BaseConstraint):
    cdef readonly dict _constraints

cdef BaseConstraint _s_tree_merge(list constraints)
cdef BaseConstraint _s_tree(TreeConstraint constraint)

cdef class CompositeConstraint(BaseConstraint):
    cdef readonly tuple _constraints

cdef void _rec_composite_iter(BaseConstraint constraint, list lst)
cdef list _r_composite_iter(BaseConstraint constraint)

cdef BaseConstraint _s_generic_merge(list constraints)
cdef BaseConstraint _s_composite(CompositeConstraint constraint)

cdef BaseConstraint _s_simplify(BaseConstraint constraint)
