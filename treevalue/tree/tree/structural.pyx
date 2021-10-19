# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from itertools import chain

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..func.cfunc cimport _c_func_treelize_run
from ..func.modes cimport _c_load_mode
from ...utils import common_direct_base

cdef class _SubsideValue:
    cpdef int size(self):
        return 1

    def __call__(self, object v):
        return v

cdef class _SubsideDict:
    def __cinit__(self, list mapping, type type_):
        self.count = 0
        self.items = []
        self.type_ = type_

        cdef str k
        cdef object v
        cdef int next_count
        for k, v in mapping:
            next_count = self.count + v.size()
            self.items.append((k, v, self.count, next_count))
            self.count = next_count

    cpdef int size(self):
        return self.count

    def __call__(self, *args):
        cdef dict _d_res = {}

        cdef str k
        cdef object v
        cdef int _i_head, _i_tail
        for k, v, _i_head, _i_tail in self.items:
            _d_res[k] = v(*args[_i_head:_i_tail])

        return self.type_(_d_res)

cdef class _SubsideArray:
    def __cinit__(self, object lst, type type_):
        self.count = 0
        self.items = []
        self.type_ = type_

        cdef object v
        cdef int next_count
        for v in lst:
            next_count = self.count + v.size()
            self.items.append((v, self.count, next_count))
            self.count = next_count

    cpdef int size(self):
        return self.count

    def __call__(self, *args):
        cdef list _l_res = []

        cdef object v
        cdef int _i_head, _i_tail
        for v, _i_head, _i_tail in self.items:
            _l_res.append(v(*args[_i_head:_i_tail]))

        return self.type_(_l_res)

_S_SUBSIDE_VALUE = _SubsideValue()

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

        return _SubsideDict(_l_subside, type(value)), chain(*_l_items), chain(*_l_types)

    elif (isinstance(value, list) and list_) or \
            (isinstance(value, tuple) and tuple_):
        for v in value:
            _s_subside, _s_items, _s_types = _c_subside_build(v, dict_, list_, tuple_)
            _l_subside.append(_s_subside)
            _l_items.append(_s_items)
            _l_types.append(_s_types)

        return _SubsideArray(_l_subside, type(value)), chain(*_l_items), chain(*_l_types)

    else:
        if isinstance(value, TreeValue):
            return _S_SUBSIDE_VALUE, (value._detach(),), (type(value),)
        else:
            return _S_SUBSIDE_VALUE, (value,), ()

STRICT = _c_load_mode('STRICT')

cdef void _c_subside_missing():
    pass

cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit):
    cdef object builder, _i_args, _i_types
    builder, _i_args, _i_types = _c_subside_build(value, dict_, list_, tuple_)
    cdef tuple args = tuple(_i_args)

    return _c_func_treelize_run(builder, args, {}, STRICT, inherit, False, _c_subside_missing), _i_types

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
    if return_type is None:
        types = set(_i_types)
        if types:
            type_ = common_direct_base(*types)
        else:
            type_ = _c_subside_keep_type
    else:
        type_ = return_type

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
    cdef list types = list(_i_types)
    if return_type is None:
        if types:
            type_ = types[0]
        else:
            type_ = _c_subside_keep_type
    else:
        type_ = return_type

    return type_(result)
