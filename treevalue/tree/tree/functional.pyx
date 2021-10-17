# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef class _ValuePathFuncWrapper:
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
    return type(t)(_c_mapping(t._detach(), _ValuePathFuncWrapper(func), ()))

cdef TreeStorage _c_filter_(TreeStorage st, object func, tuple path, bool remove_empty):
    cdef dict _d_st = st.detach()
    cdef dict _d_res = {}

    cdef str k
    cdef object v
    cdef tuple curpath
    cdef TreeStorage curst
    for k, v in _d_st.items():
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            curst = _c_filter_(v, func, curpath, remove_empty)
            if not remove_empty or not curst.empty():
                _d_res[k] = curst
        else:
            if func(v, curpath):
                _d_res[k] = v

    return TreeStorage(_d_res)

@cython.binding(True)
cpdef TreeValue filter_(TreeValue t, object func, bool remove_empty=True):
    """
    Overview:
        Filter the element in the tree with a predict function.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:`Callable`): Function for filtering
        - remove_empty (:obj:`bool`): Remove empty tree node automatically, default is `True`.

    Returns:
        - tree (:obj:`_TreeValue`): Filtered tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> filter_(t, lambda x: x < 3)                  # TreeValue({'a': 1, 'b': 2})
        >>> filter_(t, lambda x: x < 3, False)           # TreeValue({'a': 1, 'b': 2, 'x': {}})
        >>> filter_(t, lambda x: x % 2 == 1)             # TreeValue({'a': 1, 'x': {'c': 3}})
        >>> filter_(t, lambda x, p: p[0] in {'b', 'x'})  # TreeValue({'b': 2, 'x': {'c': 3, 'd': 4}})
    """
    return type(t)(_c_filter_(t._detach(), _ValuePathFuncWrapper(func), (), remove_empty))
