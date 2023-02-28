# distutils:language=c++
# cython:language_level=3

from collections import namedtuple

import cython
from libcpp cimport bool

from .base cimport _c_flatten_for_integration, _c_unflatten_for_integration
from ..tree.tree cimport TreeValue

_REGISTERED_CONTAINERS = {}

cdef inline tuple _dict_flatten(object d):
    cdef list values = []
    cdef list keys = []

    cdef object key, value
    for key, value in d.items():
        keys.append(key)
        values.append(value)

    return values, (type(d), keys)

cdef inline object _dict_unflatten(list values, tuple spec):
    cdef object type_
    cdef list keys
    type_, keys = spec

    cdef dict retval = {}
    for key, value in zip(keys, values):
        retval[key] = value

    return type_(retval)

cdef inline tuple _list_and_tuple_flatten(object l):
    return list(l), type(l)

cdef inline object _list_and_tuple_unflatten(list values, object spec):
    return spec(values)

cdef inline tuple _namedtuple_flatten(object l):
    return list(l), type(l)

cdef inline object _namedtuple_unflatten(list values, object spec):
    return spec(*values)

cdef inline tuple _treevalue_flatten(object l):
    return _c_flatten_for_integration(l)

cdef inline object _treevalue_unflatten(list values, tuple spec):
    return _c_unflatten_for_integration(values, spec)

cdef inline bool _is_namedtuple_instance(pytree) except*:
    cdef object typ = type(pytree)
    cdef tuple bases = typ.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False

    fields = getattr(typ, '_fields', None)
    if not isinstance(fields, tuple):
        return False  # pragma: no cover

    return all(type(entry) == str for entry in fields)

@cython.binding(True)
cpdef inline void register_integrate_container(object type_, object flatten_func, object unflatten_func) except*:
    """
    Overview:
        Register custom data class for generic flatten and unflatten.
    
    :param type_: Class of data to be registered.
    :param flatten_func: Function for flattening.
    :param unflatten_func: Function for unflattening.
    
    Examples::
        >>> from treevalue import register_integrate_container, generic_flatten, FastTreeValue, generic_unflatten
        >>> 
        >>> class MyDC:
        ...     def __init__(self, x, y):
        ...         self.x = x
        ...         self.y = y
        ...
        ...     def __eq__(self, other):
        ...         return isinstance(other, MyDC) and self.x == other.x and self.y == other.y
        >>> 
        >>> def _mydc_flatten(v):
        ...     return [v.x, v.y], MyDC
        >>> 
        >>> def _mydc_unflatten(v, spec):  # spec will be MyDC
        ...     return spec(*v)
        
        >>> 
        >>> register_integrate_container(MyDC, _mydc_flatten, _mydc_unflatten)  # register MyDC
        >>> 
        >>> v, spec = generic_flatten({'a': MyDC(2, 3), 'b': MyDC((4, 5), FastTreeValue({'x': 1, 'y': 'f'}))})
        >>> v
        [[2, 3], [[4, 5], [1, 'f']]]
        >>> 
        >>> rt=generic_unflatten(v, spec)
        >>> rt
        {'a': <__main__.MyDC object at 0x7fbda613f9d0>, 'b': <__main__.MyDC object at 0x7fbda6148150>}
        >>> rt['a'].x
        2
        >>> rt['a'].y
        3
        >>> rt['b'].x
        (4, 5)
        >>> rt['b'].y
        <FastTreeValue 0x7fbda5aed510>
        ├── 'x' --> 1
        └── 'y' --> 'f'
    """
    _REGISTERED_CONTAINERS[type_] = (flatten_func, unflatten_func)

cdef inline tuple _c_get_flatted_values_and_spec(object v):
    cdef list values
    cdef object spec, type_
    cdef object flatten_func
    if isinstance(v, dict):
        values, spec = _dict_flatten(v)
        type_ = dict
    elif _is_namedtuple_instance(v):
        values, spec = _namedtuple_flatten(v)
        type_ = namedtuple
    elif isinstance(v, (list, tuple)):
        values, spec = _list_and_tuple_flatten(v)
        type_ = list
    elif isinstance(v, TreeValue):
        values, spec = _treevalue_flatten(v)
        type_ = TreeValue
    elif type(v) in _REGISTERED_CONTAINERS:
        flatten_func, _ = _REGISTERED_CONTAINERS[type(v)]
        values, spec = flatten_func(v)
        type_ = type(v)
    else:
        return v, None, None

    return values, type_, spec

cdef inline object _c_get_object_from_flatted(object values, object type_, object spec):
    cdef object unflatten_func
    if type_ is dict:
        return _dict_unflatten(values, spec)
    elif type_ is namedtuple:
        return _namedtuple_unflatten(values, spec)
    elif type_ is list:
        return _list_and_tuple_unflatten(values, spec)
    elif type_ is TreeValue:
        return _treevalue_unflatten(values, spec)
    elif type_ in _REGISTERED_CONTAINERS:
        _, unflatten_func = _REGISTERED_CONTAINERS[type_]
        return unflatten_func(values, spec)
    else:
        raise TypeError(f'Unknown type for unflatten - {values!r}, {spec!r}.')  # pragma: no cover

@cython.binding(True)
cpdef inline object generic_flatten(object v):
    """
    Overview:
        Flatten generic data, including native objects, ``TreeValue``, namedtuples and custom classes \
        (see :func:`register_integrate_container`).
    
    :param v: Value to be flatted.
    :return: Flatted value.
    
    Examples::
        >>> from collections import namedtuple
        >>> from easydict import EasyDict
        >>> from treevalue import FastTreeValue, generic_flatten, generic_unflatten
        >>> 
        >>> class MyTreeValue(FastTreeValue):
        ...     pass
        >>> 
        >>> nt = namedtuple('nt', ['a', 'b'])
        >>> 
        >>> origin = {
        ...     'a': 1,
        ...     'b': (2, 3, 'f',),
        ...     'c': (2, 5, 'ds', EasyDict({  # dict's child class
        ...         'x': None,
        ...         'z': [34, '1.2'],
        ...     })),
        ...     'd': nt('f', 100),  # namedtuple
        ...     'e': MyTreeValue({'x': 1, 'y': 'dsfljk'})  # treevalue
        ... }
        >>> v, spec = generic_flatten(origin)
        >>> v
        [1, [2, 3, 'f'], [2, 5, 'ds', [None, [34, '1.2']]], ['f', 100], [1, 'dsfljk']]
        >>> 
        >>> rv = generic_unflatten(v, spec)
        >>> rv
        {'a': 1, 'b': (2, 3, 'f'), 'c': (2, 5, 'ds', {'x': None, 'z': [34, '1.2']}), 'd': nt(a='f', b=100), 'e': <MyTreeValue 0x7fb6026d7b10>
        ├── 'x' --> 1
        └── 'y' --> 'dsfljk'
        }
        >>> type(rv['c'][-1])
        <class 'easydict.EasyDict'>
    """
    values, type_, spec = _c_get_flatted_values_and_spec(v)
    if type_ is None:
        return values, (None, None, None)

    cdef list child_values = []
    cdef list child_specs = []
    cdef object value, cval, cspec
    for value in values:
        cval, cspec = generic_flatten(value)
        child_values.append(cval)
        child_specs.append(cspec)

    return child_values, (type_, spec, child_specs)

@cython.binding(True)
cpdef inline object generic_unflatten(object v, tuple gspec):
    """
    Overview:
        Inverse operation of :func:`generic_flatten`. 
    
    :param v: Flatted values.
    :param gspec: Spec data of original object.
    
    Examples::
        See :func:`generic_flatten`.
    """
    cdef object type_, spec
    cdef list child_specs
    type_, spec, child_specs = gspec
    if type_ is None:
        return v

    cdef list values = []
    cdef object _i_value, _i_spec
    for _i_value, _i_spec in zip(v, child_specs):
        values.append(generic_unflatten(_i_value, _i_spec))

    return _c_get_object_from_flatted(values, type_, spec)

@cython.binding(True)
cpdef inline object generic_mapping(object v, object func):
    """
    Overview:
        Generic map all the values, including native objects, ``TreeValue``, namedtuples and custom classes \
        (see :func:`register_integrate_container`)
    
    :param v: Original value, nested structure is supported.
    :param func: Function to operate. 
    
    Examples::
        >>> from collections import namedtuple
        >>> from easydict import EasyDict
        >>> from treevalue import FastTreeValue, generic_mapping
        >>> 
        >>> class MyTreeValue(FastTreeValue):
        ...     pass
        >>> 
        >>> nt = namedtuple('nt', ['a', 'b'])
        >>> 
        >>> origin = {
        ...     'a': 1,
        ...     'b': (2, 3, 'f',),
        ...     'c': (2, 5, 'ds', EasyDict({  # dict's child class
        ...         'x': None,
        ...         'z': [34, '1.2'],
        ...     })),
        ...     'd': nt('f', 100),  # namedtuple
        ...     'e': MyTreeValue({'x': 1, 'y': 'dsfljk'})  # treevalue
        ... }
        >>> generic_mapping(origin, str)
        {'a': '1', 'b': ('2', '3', 'f'), 'c': ('2', '5', 'ds', {'x': 'None', 'z': ['34', '1.2']}), 'd': nt(a='f', b='100'), 'e': <MyTreeValue 0x7f72e4d4ac90>
        ├── 'x' --> '1'
        └── 'y' --> 'dsfljk'
        }
    """
    values, type_, spec = _c_get_flatted_values_and_spec(v)
    if type_ is None:
        return func(values)

    cdef list retvals = []
    cdef object value
    for value in values:
        retvals.append(generic_mapping(value, func))

    return _c_get_object_from_flatted(retvals, type_, spec)
