# distutils:language=c++
# cython:language_level=3

# jsonify, clone, typetrans, walk

import copy

import cython
from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

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
    return val._detach().jsondumpx(_keep_object, False)

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
    if not callable(copy_value):
        copy_value = copy.deepcopy if copy_value else _keep_object

    return type(t)(t._detach().deepcopyx(copy_value))

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

def _p_walk(TreeStorage tree, object type_, tuple path, bool include_nodes):
    if include_nodes:
        yield path, type_(tree)

    cdef dict data = tree.detach()
    cdef str k
    cdef object v
    cdef tuple curpath
    for k, v in data.items():
        curpath = path + (k,)
        if isinstance(v, TreeStorage):
            yield from _p_walk(v, type_, curpath, include_nodes)
        else:
            yield curpath, v

@cython.binding(True)
cpdef walk(TreeValue tree, bool include_nodes=False):
    r"""
    Overview:
        Walk the values and nodes in the tree.
        The order of walk is not promised, if you need the ordered walking result, \
        just use function ``sorted`` at the outer side of :func:`walk`.

    Arguments:
        - tree: Tree value object to be walked.
        - include_nodes (:obj:`bool`): Not only the value nodes will be walked,
            but the tree nodes as well.

    Returns:
        - iter: Iterator to walk the given tree, contains 2 items, the 1st one is the full \
            path of the node, the 2nd one is the value.
    """
    return _p_walk(tree._detach(), type(tree), (), include_nodes)
