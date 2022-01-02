# distutils:language=c++
# cython:language_level=3

# flatten, unflatten

import cython

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage, _c_undelay_data

cdef void _c_flatten(TreeStorage st, tuple path, list res) except *:
    cdef dict data = st.detach()
    cdef tuple curpath

    cdef str k
    cdef object v, nv
    for k, v in data.items():
        v = _c_undelay_data(data, k, v)
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            _c_flatten(v, curpath, res)
        else:
            res.append((curpath, v))

@cython.binding(True)
cpdef list flatten(TreeValue tree):
    r"""
    Overview:
        Flatten the key-value pairs in the tree.

    Arguments:
        - tree (:obj:`TreeValue`): Tree object to be flatten.

    Returns:
        - flatted (:obj:`list`): Flatted tree, a list of tuple with (path, value).
    
    .. note::
        
        The result of function :func:`flatten` is guaranteed to be ordered, \
        which means it obey one of the tree traversal order. But please note \
        that the order of key values under the same subtree is not guaranteed.
    """
    cdef list result = []
    _c_flatten(tree._detach(), (), result)
    return result

cdef void _c_flatten_values(TreeStorage st, list res) except *:
    cdef dict data = st.detach()

    cdef str k
    cdef object v, nv
    for k, v in data.items():
        v = _c_undelay_data(data, k, v)
        if isinstance(v, TreeStorage):
            _c_flatten_values(v, res)
        else:
            res.append(v)

@cython.binding(True)
cpdef list flatten_values(TreeValue tree):
    r"""
    Overview:
        Flatten the values in the tree.

    Arguments:
        - tree (:obj:`TreeValue`): Tree object to be flatten.

    Returns:
        - flatted (:obj:`list`): Flatted tree, a list of values.
    """
    cdef list result = []
    _c_flatten_values(tree._detach(), result)
    return result

cdef void _c_flatten_keys(TreeStorage st, tuple path, list res) except *:
    cdef dict data = st.detach()
    cdef tuple curpath

    cdef str k
    cdef object v, nv
    for k, v in data.items():
        v = _c_undelay_data(data, k, v)
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            _c_flatten_keys(v, curpath, res)
        else:
            res.append(curpath)

@cython.binding(True)
cpdef list flatten_keys(TreeValue tree):
    r"""
    Overview:
        Flatten the keys in the tree.

    Arguments:
        - tree (:obj:`TreeValue`): Tree object to be flatten.

    Returns:
        - flatted (:obj:`list`): Flatted tree, a list of paths.
    """
    cdef list result = []
    _c_flatten_keys(tree._detach(), (), result)
    return result

cdef TreeStorage _c_unflatten(object pairs):
    cdef dict raw_data = {}
    cdef TreeStorage result = TreeStorage(raw_data)
    cdef list stack = []
    stack.append(((), raw_data))

    cdef tuple path
    cdef object v
    cdef tuple curpath, newpath
    cdef dict curdata, newdata
    cdef int curlen, curplen, i
    for path, v in pairs:
        curpath, curdata = stack[-1]
        while path[:len(curpath)] != curpath:
            stack.pop()
            curpath, curdata = stack[-1]

        curlen = len(curpath)
        curplen = len(path)
        for i in range(curlen, curplen):
            if i < curplen - 1:
                newpath = curpath + (path[i],)
                if path[i] not in curdata:
                    newdata = {}
                    curdata[path[i]] = TreeStorage(newdata)
                else:
                    newdata = curdata[path[i]].detach()

                curpath, curdata = newpath, newdata
                stack.append((curpath, curdata))

            else:
                curdata[path[i]] = v

    return result

@cython.binding(True)
cpdef TreeValue unflatten(object pairs, object return_type=None):
    r"""
    Overview:
        Unflatten the given pairs of tree's data.

    Arguments:
        - pairs: Data pairs, should be a iterable object with items of (path, value). 
        - return_type: Return type of unflatted tree, default is ``None`` which means use the default \
            :class:`TreeValue` class.

    Returns:
        - tree (:obj:`TreeValue`): Unflatted tree object.
    
    .. note::
        
        It is recommended to pass an ordered iterable object in ``pairs``, this \
        will improve the speed performance of function :func:`unflatten`.
        
        Because of this, it is a good idea to keep the :func:`flatten`'s result's order \
        when executing your own processing logic.
    """
    return_type = return_type or TreeValue
    return return_type(_c_unflatten(pairs))
