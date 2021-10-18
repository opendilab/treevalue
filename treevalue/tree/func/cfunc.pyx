# distutils:language=c++
# cython:language_level=3

from functools import partial

from libcpp cimport bool

from .modes cimport _e_tree_mode, _c_keyset, _c_load_mode, _c_check
from ..common.storage cimport TreeStorage
from ..tree.tree cimport TreeValue
from ...utils import SingletonMark

cdef object _c_func_treelize_run(object func, tuple args, dict kwargs,
                                 _e_tree_mode mode, object return_type, bool inherit,
                                 bool allow_missing, object missing_func):
    cdef list ck_args = []
    cdef list ck_kwargs = []
    cdef bool has_tree = False

    cdef str k
    cdef object v
    for v in args:
        if isinstance(v, TreeStorage):
            ck_args.append((v.detach(), True))
            has_tree = True
        else:
            ck_args.append((v, False))
    for k, v in kwargs.items():
        if isinstance(v, TreeStorage):
            ck_kwargs.append((k, v.detach(), True))
            has_tree = True
        else:
            ck_kwargs.append((k, v, False))

    if not has_tree:
        return func(*args, **kwargs)

    cdef dict _d_res = {}
    cdef str ak
    cdef object av
    cdef bool at
    cdef list _l_args
    cdef dict _d_kwargs
    cdef int i
    for k in tuple(_c_keyset(mode, args, kwargs)):
        _l_args = []
        for i, (av, at) in enumerate(ck_args):
            if at:
                try:
                    _l_args.append(av[k])
                except KeyError:
                    if allow_missing:
                        _l_args.append(missing_func())
                    else:
                        raise KeyError("Missing is off, key {key} not found in {item}.".format(
                            key=repr(k), item=repr(av),
                        ))
            else:
                if inherit:
                    _l_args.append(av)
                else:
                    raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                        type=repr(type(av).__name__), index=repr(i),
                    ))

        _d_kwargs = {}
        for ak, av, at in ck_kwargs:
            if at:
                try:
                    _d_kwargs[ak] = av[k]
                except KeyError:
                    if allow_missing:
                        _d_kwargs[ak] = missing_func()
                    else:
                        raise KeyError("Missing is off, key {key} not found in {item}.".format(
                            key=repr(k), item=repr(av),
                        ))
            else:
                if inherit:
                    _d_kwargs[ak] = av
                else:
                    raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                        type=repr(type(av).__name__), index=repr(ak),
                    ))

        _d_res[k] = _c_func_treelize_run(func, tuple(_l_args), _d_kwargs,
                                         mode, return_type, inherit, allow_missing, missing_func)

    return TreeStorage(_d_res)

def _w_func_treelize_run(*args, object __w_func, _e_tree_mode __w_mode, object __w_return_type,
                         bool __w_inherit, bool __w_allow_missing, object __w_missing_func, **kwargs):
    cdef tuple _a_args = tuple((item._detach() if isinstance(item, TreeValue) else item) for item in args)
    cdef dict _a_kwargs = {k: (v._detach() if isinstance(v, TreeValue) else v) for k, v in kwargs.items()}
    cdef object _st_res = _c_func_treelize_run(__w_func, _a_args, _a_kwargs, __w_mode, __w_return_type,
                                               __w_inherit, __w_allow_missing, __w_missing_func)

    if __w_return_type is not None:
        if isinstance(__w_return_type, type) and issubclass(__w_return_type, TreeValue):
            return __w_return_type(_st_res)
        else:
            return __w_return_type(args[0])(_st_res)
    else:
        return None

cpdef object _d_func_treelize(object func, _e_tree_mode mode, object return_type, bool inherit,
                       bool allow_missing, object missing_func):
    return partial(_w_func_treelize_run, __w_func=func, __w_mode=mode, __w_return_type=return_type,
                   __w_inherit=inherit, __w_allow_missing=allow_missing, __w_missing_func=missing_func)

MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")

cdef _c_common_value(object item):
    return item

cpdef object func_treelize(object mode='strict', object return_type=TreeValue,
                    bool inherit=True, object missing=MISSING_NOT_ALLOW):
    cdef _e_tree_mode _v_mode = _c_load_mode(mode)
    cdef bool allow_missing
    cdef object missing_func
    if missing is MISSING_NOT_ALLOW:
        allow_missing = False
        missing_func = None
    else:
        allow_missing = True
        missing_func = missing if callable(missing) else partial(_c_common_value, item=missing)

    _c_check(_v_mode, return_type, inherit, allow_missing, missing_func)
    return partial(_d_func_treelize, mode=_v_mode, return_type=return_type, inherit=inherit,
                   allow_missing=allow_missing, missing_func=missing_func)
