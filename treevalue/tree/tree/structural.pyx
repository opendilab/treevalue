# distutils:language=c++
# cython:language_level=3

# subside, union, rise

from itertools import chain

import cython
from hbutils.design import SingletonMark
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage, _c_undelay_data
from ..func.cfunc cimport _c_func_treelize_run, _c_missing_process
from ..func.modes cimport _c_load_mode

MISSING_NOT_ALLOW = SingletonMark("missing_not_allow")

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

cdef inline void _c_subside_missing():
    pass

cdef object _c_subside(object value, bool dict_, bool list_, bool tuple_, bool inherit,
                       object mode, object missing, bool delayed):
    cdef object builder, _i_args, _i_types
    builder, _i_args, _i_types = _c_subside_build(value, dict_, list_, tuple_)
    cdef list args = list(_i_args)

    cdef bool allow_missing
    cdef object missing_func
    allow_missing, missing_func = _c_missing_process(missing)

    return _c_func_treelize_run(_SubsideCall(builder), args, {},
                                _c_load_mode(mode), inherit, allow_missing, missing_func, delayed), _i_types

cdef inline object _c_subside_keep_type(object t):
    return t

@cython.binding(True)
cpdef object subside(object value, bool dict_=True, bool list_=True, bool tuple_=True,
                     object return_type=None, bool inherit=True,
                     object mode='strict', object missing=MISSING_NOT_ALLOW, bool delayed=False):
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
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
        - delayed (:obj:`bool`): Enable delayed mode or not, the calculation will be delayed when enabled, \
            default is ``False``, which means to all the calculation at once.

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
    result, _i_types = _c_subside(value, dict_, list_, tuple_, inherit, mode, missing, delayed)

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

def _p_union_zip(*trees):
    return trees

@cython.binding(True)
def union(*trees, object return_type=None, bool inherit=True,
          object mode='strict', object missing=MISSING_NOT_ALLOW, bool delayed=False):
    """
    Overview:
        Union tree values together.

    Arguments:
        - trees (:obj:`_TreeValue`): Tree value objects.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inheriting in wrapped function, default is `True`.
        - mode (:obj:`str`): Mode of the wrapping, default is `strict`.
        - missing (:obj:`Union[Any, Callable]`): Missing value or lambda generator of when missing, \
            default is `MISSING_NOT_ALLOW`, which means raise `KeyError` when missing detected.
        - delayed (:obj:`bool`): Enable delayed mode or not, the calculation will be delayed when enabled, \
            default is ``False``, which means to all the calculation at once.

    Returns:
        - result (:obj:`TreeValue`): Unionised tree value.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> tx = mapping(t, lambda v: v % 2 == 1)
        >>> union(t, tx)  # TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})
    """
    cdef bool allow_missing
    cdef object missing_func
    allow_missing, missing_func = _c_missing_process(missing)

    cdef list _l_trees = []
    cdef object t
    for t in trees:
        if isinstance(t, TreeValue):
            _l_trees.append(t._detach())
        else:
            _l_trees.append(t)

    cdef object result
    result = _c_func_treelize_run(_p_union_zip, _l_trees, {},
                                  _c_load_mode(mode), inherit, allow_missing, missing_func, delayed)

    cdef object type_
    if not isinstance(result, TreeStorage):
        type_ = _c_subside_keep_type
    elif return_type:
        type_ = return_type
    else:
        type_ = type(trees[0])

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
    cdef object v, nv
    cdef list _l_items, _l_values
    cdef object _i_item, _i_value
    cdef dict detached
    if isinstance(t, TreeStorage):
        detached = t.detach()
        _l_items = []
        _l_values = []
        for k, v in detached.items():
            v = _c_undelay_data(detached, k, v)
            _i_item, _i_value = _c_rise_tree_process(v)
            _l_items.append((k, _i_item))
            _l_values.append(_i_value)
        return (TreeStorage, _l_items), chain(*_l_values)
    else:
        return (object, None), (t,)

cdef object _c_rise_struct_builder(tuple p, object it):
    cdef type type_
    cdef object item
    type_, item = p

    cdef str k
    cdef object v
    cdef dict _d_res
    cdef list _l_res
    if issubclass(type_, dict):
        _d_res = {}
        for k, v in item:
            _d_res[k] = _c_rise_struct_builder(v, it)

        return type_(_d_res)
    elif issubclass(type_, (list, tuple)):
        _l_res = []
        for v in item:
            _l_res.append(_c_rise_struct_builder(v, it))

        return type_(_l_res)
    else:
        return next(it)

cdef tuple _c_rise_struct_process(list objs, object template):
    cdef type _t_type
    cdef str k
    cdef object v, item
    cdef set keys
    cdef int length
    cdef int _l_obj_0, _l_temp
    cdef object _a_template
    cdef bool failed

    if isinstance(template, (dict, type)):
        _a_template = template
    elif isinstance(template, (tuple, list)):
        if template and template[-1] is Ellipsis:
            _l_temp = len(template)
            if _l_temp < 2:
                raise TypeError(f"Ellipsis in list or tuple template should be after another "
                                f"valid template object, but length is {repr(_l_temp)}.")

            _l_obj_0 = len(objs[0])
            if _l_obj_0 < _l_temp - 2:
                raise ValueError(f"At least {repr(_l_temp - 2)} value expected due to template "
                                 f"{repr(template)}, but length is {repr(_l_obj_0)}.")

            _a_template = type(template)(chain(template[:-2], (template[-2],) * (_l_obj_0 - _l_temp + 2)))
        else:
            _a_template = template
    elif template is None:
        if not objs:
            _a_template = object
        else:
            _t_type = type(objs[0])
            if issubclass(_t_type, dict):
                keys = set(objs[0].keys())
                failed = False
                for item in objs:
                    if not isinstance(item, _t_type) or set(item.keys()) != keys:
                        failed = True
                        break

                if failed:
                    _a_template = object
                else:
                    _a_template = _t_type({k: None for k in keys})

            elif issubclass(_t_type, (list, tuple)):
                length = len(objs[0])
                failed = False
                for item in objs:
                    if not isinstance(item, _t_type) or len(item) != length:
                        failed = True
                        break

                if failed:
                    _a_template = object
                else:
                    _a_template = _t_type(None for _ in range(length))

            else:
                _a_template = object
    else:
        raise TypeError(f"Template object should be a dict, list, tuple, type or None, "
                        f"but {repr(template)} found.")

    cdef int i, j
    cdef list _r_items, _o_objs
    cdef object _i_item, _i_iter
    cdef list _r_iters = []
    if isinstance(_a_template, type):
        _t_type = _a_template
    else:
        _t_type = type(_a_template)

    if issubclass(_t_type, dict):  # dict
        keys = set(_a_template.keys())
        for item in objs:
            if not isinstance(item, _t_type):
                raise ValueError(f'Type {repr(_t_type)} expected due to template {repr(_a_template)}, '
                                 f'but {repr(item)} found.')

            if set(item.keys()) != keys:
                raise ValueError(f'Keys {repr(tuple(sorted(keys)))} expected due to template {repr(_a_template)}, '
                                 f'but {repr(tuple(sorted(item.keys())))} found.')

        _r_items = []
        _r_iters = [[] for _ in range(len(objs))]
        for k, v in _a_template.items():
            _o_objs = []
            for item in objs:
                _o_objs.append(item[k])
            _i_item, _i_iter = _c_rise_struct_process(_o_objs, v)
            _r_items.append((k, _i_item))
            for j, item in enumerate(_i_iter):
                _r_iters[j].append(item)

        return (_t_type, _r_items), [chain(*it) for it in _r_iters]
    elif issubclass(_t_type, (list, tuple)):  # list, tuple
        length = len(_a_template)
        for item in objs:
            if not isinstance(item, _t_type):
                raise ValueError(f'Type {repr(_t_type)} expected due to template {repr(_a_template)}, '
                                 f'but {repr(item)} found.')

            if len(item) != length:
                raise ValueError(f'Length {repr(length)} expected due to template {repr(_a_template)}, '
                                 f'but {repr(len(item))} found.')

        _r_items = []
        _r_iters = [[] for _ in range(len(objs))]
        for i, v in enumerate(_a_template):
            _o_objs = []
            for item in objs:
                _o_objs.append(item[i])
            _i_item, _i_iter = _c_rise_struct_process(_o_objs, v)
            _r_items.append(_i_item)
            for j, item in enumerate(_i_iter):
                _r_iters[j].append(item)

        return (_t_type, _r_items), [chain(*it) for it in _r_iters]
    else:  # object
        for item in objs:
            if not isinstance(item, _t_type):
                raise ValueError(f'Type {repr(_t_type)} expected due to template {repr(_a_template)}, '
                                 f'but {repr(item)} found.')

        _r_iters = []
        for item in objs:
            _r_iters.append((item,))

        return (object, None), _r_iters

cdef inline object _c_rise_keep_type(object t):
    return t

cdef object _c_rise(object tree, bool dict_, bool list_, bool tuple_, object template_):
    cdef object type_
    cdef object tt, iv
    if isinstance(tree, TreeValue):
        type_ = type(tree)
        tt, iv = _c_rise_tree_process(tree._detach())
    else:
        type_ = _c_rise_keep_type
        tt, iv = _c_rise_tree_process(tree)

    cdef list values = list(iv)
    cdef object ts, iis
    ts, iis = _c_rise_struct_process(values, template_)

    cdef list evals = [list(item) for item in iis]

    cdef list bvs = []
    cdef int elen = len(evals[0]) if evals else 1
    for i in range(elen):
        bvs.append(type_(_c_rise_tree_builder(tt, iter([item[i] for item in evals]))))

    return _c_rise_struct_builder(ts, iter(bvs))

@cython.binding(True)
def rise(object tree, bool dict_=True, bool list_=True, bool tuple_=True, object template=None):
    """
    Overview:
        Make the structure (dict, list, tuple) in value rise up to the top, above the tree value.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - `dict_` (:obj:`bool`): Enable dict rise, default is `True`.
        - `list_` (:obj:`bool`): Enable list rise, default is `True`.
        - `tuple_` (:obj:`bool`): Enable list rise, default is `True`.
        - template (:obj:): Rising template, default is `NO_RISE_TEMPLATE`, which means auto detect.

    Returns:
        - risen (:obj:): Risen value.

    Example:
        >>> t = TreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6, 7], 'b': [7, 8]})})
        >>> dt = rise(t)
        >>> # dt will be {'a': <TreeValue 1>, 'b': [<TreeValue 2>, <TreeValue 3>]}
        >>> # TreeValue 1 will be TreeValue({'x': [1, 2], 'y': [5, 6, 7]})
        >>> # TreeValue 2 will be TreeValue({'x': 2, 'y': 7})
        >>> # TreeValue 3 will be TreeValue({'x': 3, 'y': 8})
        >>>
        >>> t2 = TreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6], 'b': [7, 8]})})
        >>> dt2 = rise(t2)
        >>> # dt2 will be {'a': [<TreeValue 1>, <TreeValue 2>], 'b': [<TreeValue 3>, <TreeValue 4>]}
        >>> # TreeValue 1 will be TreeValue({'x': 1, 'y': 5})
        >>> # TreeValue 2 will be TreeValue({'x': 2, 'y': 6})
        >>> # TreeValue 3 will be TreeValue({'x': 2, 'y': 7})
        >>> # TreeValue 4 will be TreeValue({'x': 3, 'y': 8})
        >>>
        >>> dt3 = rise(t2, template={'a': None, 'b': None})
        >>> # dt3 will be {'a': <TreeValue 1>, 'b': <TreeValue 2>}
        >>> # TreeValue 1 will be TreeValue({'x': [1, 2], 'y': [5, 6]})
        >>> # TreeValue 2 will be TreeValue({'x': [2, 3], 'y': [7, 8]})
    """
    return _c_rise(tree, dict_, list_, tuple_, template)
