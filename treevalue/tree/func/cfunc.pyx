# distutils:language=c++
# cython:language_level=3

from functools import partial

import cython
from hbutils.design import SingletonMark
from libcpp cimport bool

from .modes cimport _e_tree_mode, _c_keyset, _c_load_mode, _c_check
from ..common.delay import delayed_partial
from ..common.delay cimport undelay
from ..common.storage cimport TreeStorage, _c_undelay_not_none_data, _c_undelay_data
from ..tree.structural cimport _c_subside, _c_rise
from ..tree.tree cimport TreeValue

_VALUE_IS_MISSING = SingletonMark('value_is_missing')
MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")



cdef inline object _c_wrap_func_treelize_run(object func, list args, dict kwargs, _e_tree_mode mode, bool inherit,
                                             bool allow_missing, object missing_func, bool delayed):
    cdef list _l_args = []
    cdef dict _d_kwargs = {}
    cdef str k, ak
    cdef object av, v, nv
    for av, k, v in args:
        _l_args.append(_c_undelay_not_none_data(av, k, v))

    for ak, (av, k, v) in kwargs.items():
        _d_kwargs[ak] = _c_undelay_not_none_data(av, k, v)

    return _c_func_treelize_run(func, _l_args, _d_kwargs,
                                mode, inherit, allow_missing, missing_func, delayed)

cdef object _c_func_treelize_run(object func, list args, dict kwargs, _e_tree_mode mode, bool inherit,
                                 bool allow_missing, object missing_func, bool delayed):
    cdef list ck_args = []
    cdef list ck_kwargs = []
    cdef bool has_tree = False

    cdef str k
    cdef object v, nv
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

    cdef list _a_args
    cdef dict _a_kwargs
    if not has_tree:
        _a_args = []
        for v in args:
            if v is not _VALUE_IS_MISSING:
                _a_args.append(v)
            else:
                _a_args.append(missing_func())

        _a_kwargs = {}
        for k, v in kwargs.items():
            if v is not _VALUE_IS_MISSING:
                _a_kwargs[k] = v
            else:
                _a_kwargs[k] = missing_func()

        return func(*_a_args, **_a_kwargs)

    cdef dict _d_res = {}
    cdef str ak
    cdef object av
    cdef bool at
    cdef list _l_args
    cdef dict _d_kwargs
    cdef int i
    for k in _c_keyset(mode, args, kwargs):
        _l_args = []
        for i, (av, at) in enumerate(ck_args):
            if at:
                try:
                    v = av[k]
                    if delayed:
                        _l_args.append((av, k, v))
                    else:
                        v = _c_undelay_data(av, k, v)
                        _l_args.append(v)
                except KeyError:
                    if allow_missing:
                        if delayed:
                            _l_args.append((None, None, _VALUE_IS_MISSING))
                        else:
                            _l_args.append(_VALUE_IS_MISSING)
                    else:
                        raise KeyError("Missing is off, key {key} not found in {item}.".format(
                            key=repr(k), item=repr(av),
                        ))
            else:
                if inherit:
                    if delayed:
                        _l_args.append((None, None, av))
                    else:
                        _l_args.append(undelay(av))
                else:
                    raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                        type=repr(type(av).__name__), index=repr(i),
                    ))

        _d_kwargs = {}
        for ak, av, at in ck_kwargs:
            if at:
                try:
                    v = av[k]
                    if delayed:
                        _d_kwargs[ak] = (av, k, v)
                    else:
                        v = _c_undelay_data(av, k, v)
                        _d_kwargs[ak] = v
                except KeyError:
                    if allow_missing:
                        if delayed:
                            _d_kwargs[ak] = (None, None, _VALUE_IS_MISSING)
                        else:
                            _d_kwargs[ak] = _VALUE_IS_MISSING
                    else:
                        raise KeyError("Missing is off, key {key} not found in {item}.".format(
                            key=repr(k), item=repr(av),
                        ))
            else:
                if inherit:
                    if delayed:
                        _d_kwargs[ak] = (None, None, av)
                    else:
                        _d_kwargs[ak] = undelay(av)
                else:
                    raise TypeError("Inherit is off, tree value expected but {type} found in args {index}.".format(
                        type=repr(type(av).__name__), index=repr(ak),
                    ))

        if delayed:
            _d_res[k] = delayed_partial(_c_wrap_func_treelize_run, func, _l_args, _d_kwargs,
                                        mode, inherit, allow_missing, missing_func, delayed)
        else:
            _d_res[k] = _c_func_treelize_run(func, _l_args, _d_kwargs,
                                             mode, inherit, allow_missing, missing_func, delayed)

    return TreeStorage(_d_res)

def _w_subside_func(object value, bool dict_=True, bool list_=True, bool tuple_=True, bool inherit=True,
                    object mode='strict', object missing=MISSING_NOT_ALLOW, bool delayed=False):
    return _c_subside(value, dict_, list_, tuple_, inherit, mode, missing, delayed)[0]

def _w_rise_func(object tree, bool dict_=True, bool list_=True, bool tuple_=True, object template=None):
    return _c_rise(tree, dict_, list_, tuple_, template)

# runtime function
def _w_func_treelize_run(*args, object __w_func, _e_tree_mode __w_mode, object __w_return_type,
                         bool __w_inherit, bool __w_allow_missing, object __w_missing_func,
                         bool __w_delayed, object __w_subside, object __w_rise, **kwargs):
    cdef list _a_args = [(item._detach() if isinstance(item, TreeValue) else item) for item in args]
    cdef dict _a_kwargs = {k: (v._detach() if isinstance(v, TreeValue) else v) for k, v in kwargs.items()}

    cdef dict _w_subside_cfg
    if __w_subside is not None:
        _w_subside_cfg = {'delayed': __w_delayed, **__w_subside}
        _a_args = [_w_subside_func(item, **_w_subside_cfg) for item in _a_args]
        _a_kwargs = {key: _w_subside_func(value, **_w_subside_cfg) for key, value in _a_kwargs.items()}

    cdef object _st_res = _c_func_treelize_run(__w_func, _a_args, _a_kwargs, __w_mode,
                                               __w_inherit, __w_allow_missing, __w_missing_func, __w_delayed)

    cdef object _o_res
    if __w_return_type is not None:
        if isinstance(_st_res, TreeStorage):
            if isinstance(__w_return_type, type) and issubclass(__w_return_type, TreeValue):
                _o_res = __w_return_type(_st_res)
            else:
                _o_res = __w_return_type(args[0])(_st_res)
        else:
            _o_res = _st_res

        if __w_rise is not None:
            _o_res = _w_rise_func(_o_res, **__w_rise)

        return _o_res
    else:
        return None

cdef object _c_common_value(object item):
    return item

cdef inline tuple _c_missing_process(object missing):
    cdef bool allow_missing
    cdef object missing_func
    if missing is MISSING_NOT_ALLOW:
        allow_missing = False
        missing_func = None
    else:
        allow_missing = True
        missing_func = missing if callable(missing) else partial(_c_common_value, missing)

    return allow_missing, missing_func

# build-time function
cpdef object _d_func_treelize(object func, object mode, object return_type, bool inherit, object missing,
                              bool delayed, object subside, object rise):
    cdef _e_tree_mode _v_mode = _c_load_mode(mode)
    cdef bool allow_missing
    cdef object missing_func
    allow_missing, missing_func = _c_missing_process(missing)

    cdef object _v_subside, _v_rise
    if subside is not None and not isinstance(subside, dict):
        _v_subside = {} if subside else None
    else:
        _v_subside = subside
    if rise is not None and not isinstance(rise, dict):
        _v_rise = {} if rise else None
    else:
        _v_rise = rise

    _c_check(_v_mode, return_type, inherit, allow_missing, missing_func)
    return partial(_w_func_treelize_run, __w_func=func, __w_mode=_v_mode, __w_return_type=return_type,
                   __w_inherit=inherit, __w_allow_missing=allow_missing, __w_missing_func=missing_func,
                   __w_delayed=delayed, __w_subside=_v_subside, __w_rise=_v_rise)

@cython.binding(True)
cpdef object func_treelize(object mode='strict', object return_type=TreeValue,
                           bool inherit=True, object missing=MISSING_NOT_ALLOW,
                           bool delayed=False, object subside=None, object rise=None):
    """
    Overview:
        Wrap a common function to tree-supported function.

    Arguments:
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - return_type (:obj:`Optional[Type[TreeClassType_]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
        - delayed (:obj:`bool`): Enable delayed mode or not, the calculation will be delayed when enabled, \
            default is ``False``, which means to all the calculation at once.
        - subside (:obj:`Union[Mapping, bool, None]`): Subside enabled to function's arguments or not, \
            and subside configuration, default is `None` which means do not use subside. \
            When subside is `True`, it will use all the default arguments in `subside` function.
        - rise (:obj:`Union[Mapping, bool, None]`): Rise enabled to function's return value or not, \
            and rise configuration, default is `None` which means do not use rise. \
            When rise is `True`, it will use all the default arguments in `rise` function. \
            (Not recommend to use auto mode when your return structure is not so strict.)

    Returns:
        - decorator (:obj:`Callable`): Wrapper for tree-supported function.

    Example:
        >>> @func_treelize()
        >>> def ssum(a, b):
        >>>     return a + b  # the a and b will be integers, not TreeValue
        >>>
        >>> t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        >>> ssum(1, 2)    # 3
        >>> ssum(t1, t2)  # TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 9}})
    """
    return partial(_d_func_treelize, mode=mode, return_type=return_type,
                   inherit=inherit, missing=missing, delayed=delayed, subside=subside, rise=rise)
