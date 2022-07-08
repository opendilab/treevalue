# distutils:language=c++
# cython:language_level=3

# jsonify, clone, typetrans, walk

import copy

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage, _c_undelay_data

cdef object _keep_object(object obj):
    return obj

@cython.binding(True)
cpdef object jsonify(TreeValue val):
    """
    Overview:
        Dump `TreeValue` object to json data.

    Arguments:
        - tree (:obj:`TreeValue`): Tree value object or tree storage object.

    Returns:
        - json (:obj:`dict`): Dumped json data.

    Example:
        >>> jsonify(TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}))  # {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    """
    return val._detach().jsondumpx(_keep_object, False, False)

@cython.binding(True)
cpdef TreeValue clone(TreeValue t, object copy_value=None):
    """
    Overview:
        Create a fully clone of the given tree.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - copy_value (:obj:`Union[None, bool, Callable, Any]`): Deep copy value or not, \
            default is `None` which means do not deep copy the values. \
            If deep copy is required, just set it to `True`.

    Returns:
        - tree (:obj:`_TreeValue`): Cloned tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> clone(t.x)  # TreeValue({'c': 3, 'd': 4})
    """
    cdef bool need_copy
    if not callable(copy_value):
        if copy_value:
            need_copy = True
            copy_value = copy.deepcopy
        else:
            need_copy = False
            copy_value = _keep_object
    else:
        need_copy = True

    return type(t)(t._detach().deepcopyx(copy_value, not need_copy))

@cython.binding(True)
cpdef TreeValue typetrans(TreeValue t, object return_type):
    """
    Overview:
        Transform tree value object to another tree value type. \
        Attention that in this function, no copy will be made, \
        the original tree value and the transformed tree value are using the same space area.

    Arguments:
        - tree (:obj:`TreeValue`): Tree value object
        - return_type (:obj:`Type[_TreeValue]`): Target tree value type

    Returns:
        - tree (:obj:`_TreeValue`): Transformed tree value object.

    Example:
        >>> t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> typetrans(t, TreeValue)  # TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    """
    if issubclass(return_type, TreeValue):
        return return_type(t._detach())
    else:
        raise TypeError("Tree value should be subclass of TreeValue, but {type} found.".format(
            type=repr(return_type.__name__)
        ))

def _p_walk(TreeStorage tree, object type_, tuple path):
    yield path, type_(tree)

    cdef dict data = tree.detach()
    cdef str k
    cdef object v, nv
    cdef tuple curpath
    for k, v in data.items():
        v = _c_undelay_data(data, k, v)
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            yield from _p_walk(v, type_, curpath)
        else:
            yield curpath, v

@cython.binding(True)
cpdef walk(TreeValue tree):
    """
    Overview:
        Walk the values and nodes in the tree.
        The order of walk is not promised, if you need the ordered walking result, \
        just use function ``sorted`` at the outer side of :func:`walk`.

    Arguments:
        - tree: Tree value object to be walked.

    Returns:
        - iter: Iterator to walk the given tree, contains 2 items, the 1st one is the full \
            path of the node, the 2nd one is the value.

    Examples:
        >>> from treevalue import TreeValue, walk
        >>> tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 2}})
        >>> for k, v in walk(tv1):
        ...     print(k, v)
        () <TreeValue 0x7f672fc53390>
        ├── 'a' --> 1
        ├── 'b' --> 2
        └── 'c' --> <TreeValue 0x7f672fc53320>
            ├── 'x' --> 2
            └── 'y' --> 2
        ('a',) 1
        ('b',) 2
        ('c',) <TreeValue 0x7f672fc53320>
        ├── 'x' --> 2
        └── 'y' --> 2
        ('c', 'x') 2
        ('c', 'y') 2
    """
    return _p_walk(tree._detach(), type(tree), ())
