# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from itertools import chain

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage
from ..func.cfunc cimport _c_func_treelize_run
from ..func.modes cimport _c_load_mode

cdef object _c_subside_process(tuple value, object it):
    cdef type type_
    cdef list items
    type_, items = value

    cdef dict _d_res
    cdef list _l_res
    cdef str k
    cdef object v
    if issubclass(type_, (list, tuple)):
        _l_res = []
        for v in items:
            _l_res.append(_c_subside_process(v, it))
        return type_(_l_res)
    elif issubclass(type_, dict):
        _d_res = {}
        for k, v in items:
            _d_res[k] = _c_subside_process(v, it)
        return type_(_d_res)
    else:
        return next(it)

cdef class _SubsideCall:
    def __cinit__(self, object run):
        self.run = run

    def __call__(self, *args):
        cdef object it = iter(args)
        return _c_subside_process(self.run, it)

cdef tuple _c_subside_build(object value, bool dict_, bool list_, bool tuple_):
    cdef str k
    cdef object v
    cdef object _s_subside, _s_items, _s_types
    cdef list _l_subside = []
    cdef list _l_items = []
    cdef list _l_types = []

    if isinstance(value, dict) and dict_:
        for k, v in value.items():
            _s_subside, _s_items, _s_types = _c_subside_build(v, dict_, list_, tuple_)
            _l_subside.append((k, _s_subside))
            _l_items.append(_s_items)
            _l_types.append(_s_types)

        return (type(value), _l_subside), chain(*_l_items), chain(*_l_types)

    elif (isinstance(value, list) and list_) or \
            (isinstance(value, tuple) and tuple_):
        for v in value:
            _s_subside, _s_items, _s_types = _c_subside_build(v, dict_, list_, tuple_)
            _l_subside.append(_s_subside)
            _l_items.append(_s_items)
            _l_types.append(_s_types)

        return (type(value), _l_subside), chain(*_l_items), chain(*_l_types)

    else:
        if isinstance(value, TreeValue):
            return (object, None), (value._detach(),), (type(value),)
        else:
            return (object, None), (value,), ()

STRICT = _c_load_mode('STRICT')

cdef void _c_subside_missing():
    pass

cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit):
    cdef object builder, _i_args, _i_types
    builder, _i_args, _i_types = _c_subside_build(value, dict_, list_, tuple_)
    cdef tuple args = tuple(_i_args)

    return _c_func_treelize_run(_SubsideCall(builder), args, {},
                                STRICT, inherit, False, _c_subside_missing), _i_types

cdef object _c_subside_keep_type(object t):
    return t

@cython.binding(True)
cpdef object subside(object value, bool dict_=True, bool list_=True, bool tuple_=True,
                     object return_type=None, bool inherit=True):
    """
    Overview:
        Drift down the structures (list, tuple, dict) down to the tree's value.

    Arguments:
        - value (:obj:): Original value object, may be nested dict, list or tuple.
        - `dict_` (:obj:`bool`): Enable dict subside, default is `True`.
        - `list_` (:obj:`bool`): Enable list subside, default is `True`.
        - `tuple_` (:obj:`bool`): Enable list subside, default is `True`.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, \
            will be auto detected when there is exactly one tree value type in this original value, \
            otherwise the default will be `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.

    Returns:
        - return (:obj:`_TreeValue`): Subsided tree value.

    Example:
        >>> data = {
        >>>     'a': TreeValue({'a': 1, 'b': 2}),
        >>>     'x': {
        >>>         'c': TreeValue({'a': 3, 'b': 4}),
        >>>         'd': [
        >>>             TreeValue({'a': 5, 'b': 6}),
        >>>             TreeValue({'a': 7, 'b': 8}),
        >>>         ]
        >>>     },
        >>>     'k': '233'
        >>> }
        >>>
        >>> tree = subside(data)
        >>> # tree should be --> TreeValue({
        >>> #    'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
        >>> #    'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        >>> #}), all structures above the tree values are subsided to the bottom of the tree.
    """
    cdef object result, _i_types
    result, _i_types = _c_subside(value, dict_, list_, tuple_, inherit)

    cdef object type_
    cdef set types
    if not isinstance(result, TreeStorage):
        type_ = _c_subside_keep_type
    elif return_type:
        type_ = return_type
    else:
        types = set(_i_types)
        if len(types) == 1:
            type_ = next(iter(types))
        else:
            type_ = TreeValue

    return type_(result)

@cython.binding(True)
def union(*trees, object return_type=None, bool inherit=True):
    """
    Overview:
        Union tree values together.

    Arguments:
        - trees (:obj:`_TreeValue`): Tree value objects.
        - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
        - missing (:obj:): Missing value or lambda generator of when missing, default is `MISSING_NOT_ALLOW`, which \
            means raise `KeyError` when missing detected.

    Returns:
        - result (:obj:`TreeValue`): Unionised tree value.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> tx = mapping(t, lambda v: v % 2 == 1)
        >>> union(t, tx)  # TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})
    """
    cdef object result, _i_types
    result, _i_types = _c_subside(tuple(trees), True, True, True, inherit)

    cdef object type_
    cdef list types
    if not isinstance(result, TreeStorage):
        type_ = _c_subside_keep_type
    elif return_type:
        type_ = return_type
    else:
        type_ = next(iter(_i_types))

    return type_(result)

cdef object _c_rise_tree_builder(tuple p, object it):
    cdef type type_
    cdef object item
    type_, item = p

    cdef str k
    cdef object v
    cdef dict _d_res
    if type_ is TreeStorage:
        _d_res = {}
        for k, v in item:
            _d_res[k] = _c_rise_tree_builder(v, it)
        return TreeStorage(_d_res)
    else:
        return next(it)

cdef tuple _c_rise_tree_process(object t):
    cdef str k
    cdef object v
    cdef list _l_items, _l_values
    cdef object _i_item, _i_value
    cdef dict detached
    if isinstance(t, TreeStorage):
        detached = t.detach()
        _l_items = []
        _l_values = []
        for k, v in detached.items():
            _i_item, _i_value = _c_rise_tree_process(v)
            _l_items.append((k, _i_item))
            _l_values.append(_i_value)
        return (TreeStorage, _l_items), chain(*_l_values)
    else:
        return (object, None), (t,)
