# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

import cython

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef class _MappingFunc:
    def __cinit__(self, func):
        self.func = func
        self.index = 2

    def __call__(self, object v, tuple path):
        while True:
            if self.index == 0:
                return self.func()

            try:
                if self.index == 1:
                    return self.func(v)
                else:
                    return self.func(v, path)
            except TypeError:
                self.index -= 1

cdef TreeStorage _c_mapping(TreeStorage st, object func, tuple path):
    cdef dict _d_st = st.detach()
    cdef dict _d_res = {}

    cdef str k
    cdef object v
    cdef tuple curpath
    for k, v in _d_st.items():
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            _d_res[k] = _c_mapping(v, func, curpath)
        else:
            _d_res[k] = func(v, curpath)

    return TreeStorage(_d_res)

@cython.binding(True)
cpdef TreeValue mapping(TreeValue t, object func):
    """
    Overview:
        Do mapping on every value in this tree.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:`Callable`): Function for mapping

    Returns:
        - tree (:obj:`_TreeValue`): Mapped tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> mapping(t, lambda x: x + 2)  # TreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
        >>> mapping(t, lambda: 1)        # TreeValue({'a': 1, 'b': 1, 'x': {'c': 1, 'd': 1}})
        >>> mapping(t, lambda x, p: p)   # TreeValue({'a': ('a',), 'b': ('b',), 'x': {'c': ('x', 'c'), 'd': ('x', 'd')}})
    """
    cdef TreeStorage _st = t._detach()
    cdef type tt = type(t)
    return tt(_c_mapping(_st, _MappingFunc(func), ()))
