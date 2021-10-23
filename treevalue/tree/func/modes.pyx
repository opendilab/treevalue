# distutils:language=c++
# cython:language_level=3

import warnings
from itertools import chain

from libcpp cimport bool

from ..common.storage cimport TreeStorage
from ..tree.tree cimport TreeValue

cdef inline _e_tree_mode _c_load_mode(str mode) except *:
    cdef upper_mode = mode.upper()

    upper_mode = mode.upper()
    if upper_mode == 'STRICT':
        return STRICT
    elif upper_mode == 'INNER':
        return INNER
    elif upper_mode == 'OUTER':
        return OUTER
    elif upper_mode == 'LEFT':
        return LEFT
    else:
        raise ValueError(f"Unknown mode - {repr(mode)}.")  # pragma: no cover

cdef inline void _c_base_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *:
    if return_type is not None:
        if not isinstance(return_type, type) and not callable(return_type):
            raise TypeError("Return type should be a type or none, but {type} found.".format(
                type=repr(type(return_type).__name__)))
        if isinstance(return_type, type) and not issubclass(return_type, TreeValue):
            raise TypeError("Tree value should be subclass of TreeValue, but {type} found.".format(
                type=repr(return_type.__name__)
            ))

cdef inline set _c_strict_keyset(list args, dict kwargs):
    cdef object k, v
    cdef dict _d_v

    cdef object first_key
    cdef set keys = None
    cdef set curkeys
    for k, v in chain(enumerate(args), kwargs.items()):
        if isinstance(v, TreeStorage):
            _d_v = v.detach()
            curkeys = set(_d_v.keys())
            if keys is None:
                first_key = k
                keys = curkeys
            else:
                if keys != curkeys:
                    raise KeyError(
                        "Argument keys not match in strict mode, key set of argument {a1} is {ks1} but {a2} in {ks2}.".format(
                            a1=repr(first_key), ks1=repr(keys),
                            a2=repr(k), ks2=repr(curkeys),
                        ))

    return keys

cdef inline void _c_strict_check(_e_tree_mode mode, object return_type,
                          bool inherit, bool allow_missing, object missing_func) except *:
    _c_base_check(mode, return_type, inherit, allow_missing, missing_func)
    if allow_missing:
        warnings.warn(RuntimeWarning("Allow missing detected, but cannot applied in strict mode."))

cdef inline set _c_inner_keyset(list args, dict kwargs):
    cdef object k, v
    cdef dict _d_v

    cdef object first_key
    cdef set keys = None
    cdef set curkeys
    for k, v in chain(enumerate(args), kwargs.items()):
        if isinstance(v, TreeStorage):
            _d_v = v.detach()
            curkeys = set(_d_v.keys())
            if keys is None:
                keys = curkeys
            else:
                keys &= curkeys

    return keys

cdef inline void _c_inner_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *:
    _c_base_check(mode, return_type, inherit, allow_missing, missing_func)

cdef inline set _c_outer_keyset(list args, dict kwargs):
    cdef object k, v
    cdef dict _d_v

    cdef object first_key
    cdef set keys = None
    cdef set curkeys
    for k, v in chain(enumerate(args), kwargs.items()):
        if isinstance(v, TreeStorage):
            _d_v = v.detach()
            curkeys = set(_d_v.keys())
            if keys is None:
                keys = curkeys
            else:
                keys |= curkeys

    return keys

cdef inline void _c_outer_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *:
    _c_base_check(mode, return_type, inherit, allow_missing, missing_func)
    if not allow_missing:
        warnings.warn(RuntimeWarning("Missing is still not allowed, but this may cause KeyError in outer mode."))

cdef inline set _c_left_keyset(list args, dict kwargs):
    cdef object k, v
    cdef dict _d_v

    cdef object first_key
    for k, v in chain(enumerate(args), sorted(kwargs.items())):
        if isinstance(v, TreeStorage):
            _d_v = v.detach()
            return set(_d_v.keys())

    return set()  # pragma: no cover

cdef inline void _c_left_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *:
    _c_base_check(mode, return_type, inherit, allow_missing, missing_func)

cdef inline set _c_keyset(_e_tree_mode mode, list args, dict kwargs):
    if mode == STRICT:
        return _c_strict_keyset(args, kwargs)
    elif mode == INNER:
        return _c_inner_keyset(args, kwargs)
    elif mode == OUTER:
        return _c_outer_keyset(args, kwargs)
    else:
        return _c_left_keyset(args, kwargs)

cdef inline void _c_check(_e_tree_mode mode, object return_type,
                   bool inherit, bool allow_missing, object missing_func) except *:
    if mode == STRICT:
        _c_strict_check(mode, return_type, inherit, allow_missing, missing_func)
    elif mode == INNER:
        _c_inner_check(mode, return_type, inherit, allow_missing, missing_func)
    elif mode == OUTER:
        _c_outer_check(mode, return_type, inherit, allow_missing, missing_func)
    else:
        _c_left_check(mode, return_type, inherit, allow_missing, missing_func)
