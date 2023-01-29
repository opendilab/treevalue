# distutils:language=c++
# cython:language_level=3
import os

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage, _c_undelay_data

cdef class _WrappedConstraintException(Exception):
    pass

cdef class Constraint:
    cpdef void _validate_node(self, object instance) except*:
        raise NotImplementedError  # pragma: no cover

    cpdef void _validate_value(self, object instance) except*:
        raise NotImplementedError  # pragma: no cover

    cpdef object _features(self):
        raise NotImplementedError  # pragma: no cover

    cpdef bool _contains(self, Constraint other):
        raise NotImplementedError  # pragma: no cover

    cpdef Constraint _transaction(self, str key):
        raise NotImplementedError  # pragma: no cover

    @cython.final
    cdef inline bool _feature_match(self, Constraint other):
        return type(self) == type(other) and self._features() == other._features()

    @cython.final
    cdef inline bool _contains_check(self, Constraint other):
        return isinstance(other, EmptyConstraint) or self._feature_match(other) or self._contains(other)

    @cython.final
    cdef inline tuple _native_validate(self, object instance, type type_, list path):
        cdef dict raw
        cdef str key
        cdef object value
        cdef Constraint subcons

        cdef bool retval
        cdef tuple retpath
        cdef Constraint retcons
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
                value = _c_undelay_data(raw, key, value)
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
        cdef Constraint retcons
        cdef Exception reterr
        retval, retpath, retcons, reterr = self.check(instance)

        if not retval:
            raise reterr

    def __eq__(self, other):
        return self._feature_match(to_constraint(other))

    def __hash__(self):
        return hash(self._features())

    cpdef bool equiv(self, object other):
        cdef Constraint c = to_constraint(other)
        return self._contains_check(c) and c._contains_check(self)

    def _yield_accessible(self, __type, *args, **kwargs):
        if isinstance(__type, type) and issubclass(__type, Constraint):
            if _c_default_accessible(self, __type, args, kwargs):
                yield self
        else:
            if __type(self, *args, **kwargs):
                yield self

    def access_first(self, __type, *args, **kwargs):
        iter_ = self._yield_accessible(__type, *args, **kwargs)
        try:
            return next(iter_)
        except StopIteration:
            return _EMPTY_CONSTRAINT

    def access_all(self, __type, *args, **kwargs):
        cdef list retval = []
        cdef Constraint cons
        for cons in self._yield_accessible(__type, *args, **kwargs):
            retval.append(cons)
        return retval

    def __ge__(self, other):
        cdef Constraint c = to_constraint(other)
        return self._contains_check(c)

    def __gt__(self, other):
        cdef Constraint c = to_constraint(other)
        return self._contains_check(c) and not c._contains_check(self)

    def __le__(self, other):
        cdef Constraint c = to_constraint(other)
        return c._contains_check(self)

    def __lt__(self, other):
        cdef Constraint c = to_constraint(other)
        return c._contains_check(self) and not self._contains_check(c)

    def __repr__(self):
        return f'<{type(self).__name__} {self._features()!r}>'

cdef inline bool _c_default_accessible(Constraint cons, object type_, tuple items, dict params) except*:
    if type(cons) != type_:
        return False

    cdef int i
    cdef str key
    cdef object value
    for i, value in enumerate(items):
        try:
            if cons[i] != value:
                return False
        except (KeyError, IndexError, TypeError):
            return False

    for key, value in params.items():
        if not hasattr(cons, key) or getattr(cons, key) != value:
            return False

    return True

@cython.final
cdef class EmptyConstraint(Constraint):
    cpdef inline void _validate_node(self, object instance) except*:
        pass

    cpdef inline void _validate_value(self, object instance) except*:
        pass

    cpdef inline object _features(self):
        return ()

    cpdef inline bool _contains(self, Constraint other):
        return isinstance(other, EmptyConstraint)

    cpdef inline Constraint _transaction(self, str key):
        return self

    def _yield_accessible(self, __type, *args, **kwargs):
        yield from []

    def __bool__(self):
        return False

    def __repr__(self):
        return f'<{type(self).__name__}>'

_EMPTY_CONSTRAINT = EmptyConstraint()

cdef inline Constraint _r_parse_cons(object obj):
    if isinstance(obj, Constraint):
        return obj
    elif obj is None:
        return _EMPTY_CONSTRAINT
    elif isinstance(obj, type):
        return TypeConstraint(obj)
    elif isinstance(obj, (list, tuple)):
        return CompositeConstraint([_r_parse_cons(c) for c in obj])
    elif isinstance(obj, dict):
        return TreeConstraint({key: _r_parse_cons(value) for key, value in obj.items()})
    else:
        raise TypeError(f'Invalid constraint - {obj!r}.')

cpdef inline Constraint to_constraint(object obj):
    if obj is None:
        return _EMPTY_CONSTRAINT
    else:
        return _s_simplify(_r_parse_cons(obj))

cdef class ValueConstraint(Constraint):
    cpdef void _validate_node(self, object instance) except*:
        pass

    cpdef Constraint _transaction(self, str key):
        return self

cdef class NodeConstraint(Constraint):
    cpdef void _validate_value(self, object instance) except*:
        raise TypeError(f'TreeValue node expected, but value {instance!r} found.')

    cpdef Constraint _transaction(self, str key):
        return _EMPTY_CONSTRAINT

cdef class TypeConstraint(ValueConstraint):
    def __cinit__(self, object type_):
        assert isinstance(type_, type), f'A type class expected, but {type_!r} given.'
        self.type_ = type_

    cpdef void _validate_value(self, object instance) except*:
        if not isinstance(instance, self.type_):
            raise TypeError(f'Invalid type, {self.type_!r} expected but {type(instance)!r} found - {instance!r}.')

    cpdef object _features(self):
        return self.type_

    cpdef bool _contains(self, Constraint other):
        return isinstance(other, TypeConstraint) and issubclass(self.type_, other.type_)

    def __reduce__(self):
        return TypeConstraint, (self.type_,)

cdef inline str _c_func_fullname(object f):
    cdef str fname = f.__name__
    cdef str mname = getattr(f, '__module__', '')
    return f'{mname}.{fname}' if mname else fname

cdef class ValueFuncConstraint(ValueConstraint):
    def __cinit__(self, object func, str name):
        self.func = func
        self.name = name

    cpdef object _features(self):
        return self.name, self.func

    cpdef bool _contains(self, Constraint other):
        return type(self) == type(other) and self.func == other.func

    def __repr__(self):
        return f'<{type(self).__name__} {self.name}>'

    def __reduce__(self):
        return type(self), (self.func, self.name)

@cython.final
cdef class ValueValidateConstraint(ValueFuncConstraint):
    cpdef inline void _validate_value(self, object instance) except*:
        self.func(instance)

@cython.final
cdef class ValueCheckConstraint(ValueFuncConstraint):
    cpdef inline void _validate_value(self, object instance) except*:
        assert self.func(instance), f'Check of {self.name!r} failed.'

cpdef inline ValueValidateConstraint vval(object func, object name=None):
    return ValueValidateConstraint(func, str(name or _c_func_fullname(func)))

cpdef inline ValueCheckConstraint vcheck(object func, object name=None):
    return ValueCheckConstraint(func, str(name or _c_func_fullname(func)))

@cython.final
cdef class LeafConstraint(Constraint):
    cpdef inline void _validate_node(self, object instance) except*:
        raise TypeError(f'TreeValue leaf expected, but node found:{os.linesep}{instance!r}.')

    cpdef inline void _validate_value(self, object instance) except*:
        pass

    cpdef inline object _features(self):
        return None

    cpdef inline bool _contains(self, Constraint other):
        return isinstance(other, LeafConstraint)

    cpdef inline Constraint _transaction(self, str key):
        return _EMPTY_CONSTRAINT  # pragma: no cover

    def __repr__(self):
        return f'<{type(self).__name__}>'

cpdef inline LeafConstraint cleaf():
    return LeafConstraint()

cdef class NodeFuncConstraint(NodeConstraint):
    def __cinit__(self, object func, str name):
        self.func = func
        self.name = name

    cpdef object _features(self):
        return self.name, self.func

    cpdef bool _contains(self, Constraint other):
        return type(self) == type(other) and self.func == other.func

    def __repr__(self):
        return f'<{type(self).__name__} {self.name}>'

    def __reduce__(self):
        return type(self), (self.func, self.name)

@cython.final
cdef class NodeValidateConstraint(NodeFuncConstraint):
    cpdef inline void _validate_node(self, object instance) except*:
        self.func(instance)

@cython.final
cdef class NodeCheckConstraint(NodeFuncConstraint):
    cpdef inline void _validate_node(self, object instance) except*:
        assert self.func(instance), f'Check of {self.name!r} failed.'

cpdef inline NodeValidateConstraint nval(object func, object name=None):
    return NodeValidateConstraint(func, str(name or _c_func_fullname(func)))

cpdef inline NodeCheckConstraint ncheck(object func, object name=None):
    return NodeCheckConstraint(func, str(name or _c_func_fullname(func)))

cdef class TreeConstraint(Constraint):
    def __cinit__(self, dict constraints, bool need_sort=True):
        if need_sort:
            self._constraints = {key: constraints[key] for key in sorted(constraints.keys())}
        else:
            self._constraints = dict(constraints)

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

    cpdef bool _contains(self, Constraint other):
        cdef str key
        cdef Constraint _s_cons, _o_cons
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

    cpdef Constraint _transaction(self, str key):
        if key in self._constraints:
            return self._constraints[key]
        else:
            return _EMPTY_CONSTRAINT

    def _yield_accessible(self, __type, *args, **kwargs):
        yield from []

    def __reduce__(self):
        return TreeConstraint, (self._constraints, False)

cdef inline Constraint _s_tree_merge(list constraints):
    cdef dict cmap = {}
    cdef str key
    cdef Constraint cons
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
        cons = _s_generic_merge(clist)
        if cons:
            fmap[key] = cons

    if fmap:
        return TreeConstraint(fmap)
    else:
        return _EMPTY_CONSTRAINT

cdef inline Constraint _s_tree(TreeConstraint constraint):
    cdef dict dcons = {}
    cdef list keys = sorted(constraint._constraints.keys())
    cdef str key
    cdef Constraint cons, pcons
    for key in keys:
        pcons = _s_simplify(constraint._constraints[key])
        if not isinstance(pcons, EmptyConstraint):
            dcons[key] = pcons

    if dcons:
        return TreeConstraint(dcons)
    else:
        return _EMPTY_CONSTRAINT

cdef class CompositeConstraint(Constraint):
    def __cinit__(self, list constraints, bool need_sort=True):
        if need_sort:
            self._constraints = tuple(sorted(constraints, key=lambda x: repr(x._features())))
        else:
            self._constraints = tuple(constraints)

    cpdef void _validate_node(self, object instance) except*:
        cdef Constraint cons
        for cons in self._constraints:
            try:
                cons._validate_node(instance)
            except _WrappedConstraintException:
                raise
            except Exception as err:
                raise _WrappedConstraintException(err, cons)

    cpdef void _validate_value(self, object instance) except*:
        cdef Constraint cons
        for cons in self._constraints:
            try:
                cons._validate_value(instance)
            except _WrappedConstraintException:
                raise
            except Exception as err:
                raise _WrappedConstraintException(err, cons)

    cpdef object _features(self):
        return self._constraints

    cpdef bool _contains(self, Constraint other):
        cdef Constraint cons, pcons
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

    cpdef Constraint _transaction(self, str key):
        return CompositeConstraint([c._transaction(key) for c in self._constraints])

    def _yield_accessible(self, __type, *args, **kwargs):
        cdef Constraint cons
        for cons in self._constraints:
            yield from cons._yield_accessible(__type, *args, **kwargs)

    def __reduce__(self):
        return CompositeConstraint, (list(self._constraints), False)

    def __iter__(self):
        return iter(self._constraints)

cdef inline void _rec_composite_iter(Constraint constraint, list lst):
    cdef Constraint cons
    if isinstance(constraint, CompositeConstraint):
        for cons in constraint._constraints:
            _rec_composite_iter(cons, lst)
    else:
        lst.append(constraint)

cdef inline list _r_composite_iter(Constraint constraint):
    cdef list lst = []
    _rec_composite_iter(constraint, lst)
    return lst

cdef inline Constraint _s_generic_merge(list constraints):
    cdef Constraint gcons, cons, pcons
    cdef list sins = []
    cdef list trees = []
    for gcons in constraints:
        for cons in _r_composite_iter(gcons):
            pcons = _s_simplify(cons)
            if isinstance(pcons, TreeConstraint):
                trees.append(pcons)
            elif not isinstance(pcons, EmptyConstraint):
                sins.append(pcons)

    cdef Constraint tree = _s_tree_merge(trees)
    if not isinstance(tree, EmptyConstraint):
        sins.append(tree)

    if not sins:
        return _EMPTY_CONSTRAINT

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

    assert finals, 'Finals should not be empty, but it\'s empty actually.'
    if len(finals) == 1:
        return finals[0]
    else:
        return CompositeConstraint(finals)

cdef inline Constraint _s_composite(CompositeConstraint constraint):
    return _s_generic_merge(list(constraint._constraints))

cdef inline Constraint _s_simplify(Constraint constraint):
    if isinstance(constraint, CompositeConstraint):
        return _s_composite(constraint)
    elif isinstance(constraint, TreeConstraint):
        return _s_tree(constraint)
    else:
        return constraint

cpdef inline Constraint transact(object cons, str key):
    cdef Constraint constraint
    if isinstance(cons, EmptyConstraint):
        return _EMPTY_CONSTRAINT
    else:
        constraint = to_constraint(cons)
        # noinspection PyProtectedMember
        return _s_simplify(constraint._transaction(key))
