# distutils:language=c++
# cython:language_level=3

from ..tree.flatten cimport _c_flatten, _c_unflatten

cdef inline tuple _c_flatten_for_integration(object tv):
    cdef list result = []
    _c_flatten(tv._detach(), (), result)

    cdef list paths = []
    cdef list values = []
    for path, value in result:
        paths.append(path)
        values.append(value)

    return values, (type(tv), paths)

cdef inline object _c_unflatten_for_integration(object values, tuple spec):
    cdef object type_
    cdef list paths
    type_, paths = spec
    return type_(_c_unflatten(zip(paths, values)))
