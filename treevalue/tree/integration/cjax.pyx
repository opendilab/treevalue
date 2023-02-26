# distutils:language=c++
# cython:language_level=3

import cython

from ..tree.flatten cimport _c_flatten, _c_unflatten
from ..tree.tree cimport TreeValue

cdef inline tuple _c_flatten_for_jax(object tv):
    cdef list result = []
    _c_flatten(tv._detach(), (), result)

    cdef list paths = []
    cdef list values = []
    for path, value in result:
        paths.append(path)
        values.append(value)

    return values, (type(tv), paths)

cdef inline object _c_unflatten_for_jax(tuple aux, tuple values):
    cdef object type_
    cdef list paths
    type_, paths = aux
    return type_(_c_unflatten(zip(paths, values)))

@cython.binding(True)
cpdef void register_for_jax(object cls) except*:
    """
    Overview:
        Register treevalue class for jax.
    
    :param cls: TreeValue class.
    
    Examples::
        >>> from treevalue import FastTreeValue, TreeValue, register_for_jax
        >>> register_for_jax(TreeValue)
        >>> register_for_jax(FastTreeValue)
    
    .. warning::
        This method will put a warning message and then do nothing when jax is not installed.
    """
    if isinstance(cls, type) and issubclass(cls, TreeValue):
        import jax
        jax.tree_util.register_pytree_node(cls, _c_flatten_for_jax, _c_unflatten_for_jax)
    else:
        raise TypeError(f'Registered class should be a subclass of TreeValue, but {cls!r} found.')
