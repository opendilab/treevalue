# distutils:language=c++
# cython:language_level=3

import cython

from .base cimport _c_flatten_for_integration, _c_unflatten_for_integration
from ..tree.tree cimport TreeValue

cdef inline tuple _c_flatten_for_torch(object tv):
    return _c_flatten_for_integration(tv)

cdef inline object _c_unflatten_for_torch(list values, tuple context):
    return _c_unflatten_for_integration(values, context)

@cython.binding(True)
cpdef void register_for_torch(object cls) except*:
    """
    Overview:
        Register treevalue class for torch's pytree library.

    :param cls: TreeValue class.

    Examples::
        >>> from treevalue import FastTreeValue, TreeValue, register_for_torch
        >>> register_for_torch(TreeValue)
        >>> register_for_torch(FastTreeValue)

    .. warning::
        This method will put a warning message and then do nothing when torch is not installed.
    """
    if isinstance(cls, type) and issubclass(cls, TreeValue):
        import torch
        torch.utils._pytree._register_pytree_node(cls, _c_flatten_for_torch, _c_unflatten_for_torch)
    else:
        raise TypeError(f'Registered class should be a subclass of TreeValue, but {cls!r} found.')
