# distutils:language=c++
# cython:language_level=3
import os

from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef class _WrappedConstraintException(Exception):
    pass

cdef class BaseConstraint:
    cpdef void _validate_node(self, object instance) except*:
        raise NotImplementedError  # pragma: no cover

    cpdef void _validate_value(self, object instance) except*:
        raise NotImplementedError  # pragma: no cover

    cpdef object _features(self):
        raise NotImplementedError  # pragma: no cover

    cpdef bool _contains(self, BaseConstraint other):
        raise NotImplementedError  # pragma: no cover

    cpdef BaseConstraint _transaction(self, str key):
        raise NotImplementedError  # pragma: no cover

    cdef inline bool _feature_match(self, BaseConstraint other):
        return type(self) == type(other) and self._features() == other._features()

    cdef inline bool _contains_check(self, BaseConstraint other):
        return isinstance(other, EmptyConstraint) or self._feature_match(other) or self._contains(other)

    cdef tuple _native_validate(self, object instance, type type_, list path):
        cdef dict raw
        cdef str key
        cdef object value
        cdef BaseConstraint subcons

        cdef bool retval
        cdef tuple retpath
        cdef BaseConstraint retcons
        cdef Exception reterr

        if isinstance(instance, TreeStorage):
            try:
                self._validate_node(type_(instance))
            except _WrappedConstraintException as err:
                reterr, retcons = err.args
                return False, tuple(path), retcons, reterr
            except Exception as err:
                return False, tuple(path), self, err

            raw = instance.detach()
            for key, value in raw.items():
                path.append(key)
                subcons = self._transaction(key)
                retval, retpath, retcons, reterr = subcons._native_validate(raw[key], type_, path)
                path.pop()
                if not retval:
                    return retval, retpath, retcons, reterr
        else:
            try:
                self._validate_value(instance)
            except _WrappedConstraintException as err:
                reterr, retcons = err.args
                return False, tuple(path), retcons, reterr
            except Exception as err:
                return False, tuple(path), self, err

        return True, None, None, None

    cpdef tuple check(self, object instance):
        cdef list path = []
        if isinstance(instance, TreeValue):
            return self._native_validate(instance._detach(), type(instance), path)
        else:
            return self._native_validate(instance, TreeValue, path)

    def validate(self, object instance):
        cdef bool retval
        cdef tuple retpath
        cdef BaseConstraint retcons
        cdef Exception reterr
        retval, retpath, retcons, reterr = self.check(instance)

        cdef tuple args, fargs
        cdef list pargs
        cdef object msg
        if not retval:
            args = reterr.args
            if args:
                msg, *pargs = args
                fargs = (msg, (retpath, retcons), *pargs)
            else:
                fargs = (retpath,)

            raise type(reterr)(*fargs)

    def __eq__(self, other):
        return self._feature_match(to_constraint(other))

    def __hash__(self):
        return hash(self._features())

    cpdef bool equiv(self, object other):
        cdef BaseConstraint c = to_constraint(other)
        return self._contains_check(c) and c._contains_check(self)

    def __ge__(self, other):
        cdef BaseConstraint c = to_constraint(other)
        return self._contains_check(c)

    def __gt__(self, other):
        cdef BaseConstraint c = to_constraint(other)
        return self._contains_check(c) and not c._contains_check(self)

    def __le__(self, other):
        cdef BaseConstraint c = to_constraint(other)
        return c._contains_check(self)

    def __lt__(self, other):
        cdef BaseConstraint c = to_constraint(other)
        return c._contains_check(self) and not self._contains_check(c)

    def __repr__(self):
        return f'<{type(self).__name__} {self._features()!r}>'

cdef inline BaseConstraint _r_parse_cons(object obj):
    if isinstance(obj, BaseConstraint):
        return obj
    elif obj is None:
        return EmptyConstraint()
    elif isinstance(obj, type):
        return TypeConstraint(obj)
    elif isinstance(obj, (list, tuple)):
        return CompositeConstraint([_r_parse_cons(c) for c in obj])
    elif isinstance(obj, dict):
        return TreeConstraint({key: _r_parse_cons(value) for key, value in obj.items()})
    else:
        raise TypeError(f'Invalid constraint - {obj!r}.')

cpdef inline BaseConstraint to_constraint(object obj):
    return _s_simplify(_r_parse_cons(obj))

cdef class EmptyConstraint(BaseConstraint):
    cpdef void _validate_node(self, object instance) except*:
        pass

    cpdef void _validate_value(self, object instance) except*:
        pass

    cpdef object _features(self):
        return ()

    cpdef bool _contains(self, BaseConstraint other):
        return isinstance(other, EmptyConstraint)

    cpdef BaseConstraint _transaction(self, str key):
        return self

    def __bool__(self):
        return False

    def __repr__(self):
        return f'<{type(self).__name__}>'

cdef class ValueConstraint(BaseConstraint):
    cpdef void _validate_node(self, object instance) except*:
        pass

    cpdef BaseConstraint _transaction(self, str key):
        return self

cdef class NodeConstraint(BaseConstraint):
    cpdef void _validate_value(self, object instance) except*:
        raise TypeError(f'TreeValue node expected, but value {instance!r} found.')

    cpdef BaseConstraint _transaction(self, str key):
        return EmptyConstraint()

cdef class TypeConstraint(ValueConstraint):
    def __cinit__(self, type type_):
        self.type_ = type_

    cpdef void _validate_value(self, object instance) except*:
        if not isinstance(instance, self.type_):
            raise TypeError(f'Invalid type, {self.type_!r} expected but {type(instance)!r} found - {instance!r}.')

    cpdef object _features(self):
        return self.type_

    cpdef bool _contains(self, BaseConstraint other):
        return isinstance(other, TypeConstraint) and issubclass(self.type_, other.type_)

cdef class LeafConstraint(BaseConstraint):
    cpdef void _validate_node(self, object instance) except*:
        raise TypeError(f'TreeValue leaf expected, but node found:{os.linesep}{instance!r}.')

    cpdef void _validate_value(self, object instance) except*:
        pass

    cpdef object _features(self):
        return None

    cpdef bool _contains(self, BaseConstraint other):
        return isinstance(other, LeafConstraint)

    cpdef BaseConstraint _transaction(self, str key):
        return EmptyConstraint()

    def __repr__(self):
        return f'<{type(self).__name__}>'

cpdef inline LeafConstraint cleaf():
    return LeafConstraint()

cdef class TreeConstraint(BaseConstraint):
    def __cinit__(self, dict constraints):
        self._constraints = {key: constraints[key] for key in sorted(constraints.keys())}

    cpdef void _validate_node(self, object instance) except*:
        pass

    cpdef void _validate_value(self, object instance) except*:
        raise TypeError(f'TreeValue node expected, but value {instance!r} found.')

    cpdef object _features(self):
        cdef str key
        cdef list ft = []
        for key in self._constraints:
            ft.append((key, self._constraints[key]))
        return tuple(ft)

    cpdef bool _contains(self, BaseConstraint other):
        cdef str key
        cdef BaseConstraint _s_cons, _o_cons
        cdef list _f_keys
        if isinstance(other, TreeConstraint):
            _f_keys = sorted(set(self._constraints.keys()) | set(other._constraints.keys()))
            for key in _f_keys:
                _s_cons = self._transaction(key)
                _o_cons = other._transaction(key)
                if not (_s_cons >= _o_cons):
                    return False

            return True
        else:
            return False

    cpdef BaseConstraint _transaction(self, str key):
        if key in self._constraints:
            return self._constraints[key]
        else:
            return EmptyConstraint()

cdef inline BaseConstraint _s_tree_merge(list constraints):
    cdef dict cmap = {}
    cdef str key
    cdef BaseConstraint cons
    cdef TreeConstraint tcons
    for tcons in constraints:
        for key, cons in tcons._constraints.items():
            if key not in cmap:
                cmap[key] = [cons]
            else:
                cmap[key].append(cons)

    cdef list clist
    cdef dict fmap = {}
    for key, clist in cmap.items():
        cons = _s_composite(clist)
        if not cons:
            fmap[key] = cons

    if fmap:
        return TreeConstraint(fmap)
    else:
        return EmptyConstraint()

cdef inline BaseConstraint _s_tree(TreeConstraint constraint):
    cdef dict dcons = {}
    cdef list keys = sorted(constraint._constraints.keys())
    cdef str key
    cdef BaseConstraint cons, pcons
    for key in keys:
        pcons = _s_simplify(constraint._constraints[key])
        if not isinstance(pcons, EmptyConstraint):
            dcons[key] = pcons

    if dcons:
        return TreeConstraint(dcons)
    else:
        return EmptyConstraint()

cdef class CompositeConstraint(BaseConstraint):
    def __cinit__(self, list constraints):
        self._constraints = tuple(sorted(constraints, key=lambda x: repr(x._features())))

    cpdef void _validate_node(self, object instance) except*:
        cdef BaseConstraint cons
        for cons in self._constraints:
            try:
                cons._validate_node(instance)
            except _WrappedConstraintException:
                raise
            except Exception as err:
                raise _WrappedConstraintException(err, cons)

    cpdef void _validate_value(self, object instance) except*:
        cdef BaseConstraint cons
        for cons in self._constraints:
            try:
                cons._validate_value(instance)
            except _WrappedConstraintException:
                raise
            except Exception as err:
                raise _WrappedConstraintException(err, cons)

    cpdef object _features(self):
        return self._constraints

    cpdef bool _contains(self, BaseConstraint other):
        cdef BaseConstraint cons, pcons
        cdef bool found_contains
        if isinstance(other, CompositeConstraint):
            for pcons in other._constraints:
                found_contains = False
                for cons in self._constraints:
                    if cons >= pcons:
                        found_contains = True
                        break

                if not found_contains:
                    return False

            return True
        else:
            for cons in self._constraints:
                if cons >= other:
                    return True

            return False

    cpdef BaseConstraint _transaction(self, str key):
        return CompositeConstraint([c._transaction(key) for c in self._constraints])

cdef inline void _rec_composite_iter(BaseConstraint constraint, list lst):
    cdef BaseConstraint cons
    if isinstance(constraint, CompositeConstraint):
        for cons in constraint._constraints:
            if isinstance(cons, CompositeConstraint):
                _rec_composite_iter(cons, lst)
            else:
                lst.append(cons)
    else:
        lst.append(constraint)

cdef inline list _r_composite_iter(BaseConstraint constraint):
    cdef list lst = []
    _rec_composite_iter(constraint, lst)
    return lst

cdef inline BaseConstraint _s_generic_merge(list constraints):
    cdef BaseConstraint gcons, cons, pcons
    cdef list sins = []
    cdef list trees = []
    for gcons in constraints:
        for cons in _r_composite_iter(gcons):
            pcons = _s_simplify(cons)
            if isinstance(pcons, TreeConstraint):
                trees.append(pcons)
            elif not isinstance(pcons, EmptyConstraint):
                sins.append(pcons)

    cdef BaseConstraint tree = _s_tree_merge(trees)
    if not isinstance(tree, EmptyConstraint):
        sins.append(tree)

    if not sins:
        return EmptyConstraint()

    cdef int i, j
    cdef set _child_ids = set()
    cdef int n = len(sins)
    for i in range(n):
        if i in _child_ids:
            continue
        for j in range(n):
            if i == j or j in _child_ids:
                continue
            if sins[i] >= sins[j]:
                _child_ids.add(j)

    cdef list finals = []
    for i in range(n):
        if i not in _child_ids:
            finals.append(sins[i])

    if not finals:
        return EmptyConstraint()
    elif len(finals) == 1:
        return finals[0]
    else:
        return CompositeConstraint(finals)

cdef inline BaseConstraint _s_composite(CompositeConstraint constraint):
    return _s_generic_merge(list(constraint._constraints))

cdef inline BaseConstraint _s_simplify(BaseConstraint constraint):
    if isinstance(constraint, CompositeConstraint):
        return _s_composite(constraint)
    elif isinstance(constraint, TreeConstraint):
        return _s_tree(constraint)
    else:
        return constraint
