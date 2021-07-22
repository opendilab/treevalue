from typing import TypeVar, List, Type

from .tree import TreeValue, get_data_property

_TreeValue = TypeVar("_TreeValue", bound=TreeValue)


def jsonify(tree: _TreeValue):
    """
    Overview:
        Dump `TreeValue` object to json data.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object.

    Returns:
        - json (:obj:`dict`): Dumped json data.

    Example:
        >>> jsonify(TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}))  # {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    """
    return get_data_property(tree).json()


def view(tree: _TreeValue, path: List[str]) -> _TreeValue:
    """
    Overview:
        Create a `TreeValue` object which is a view of given tree.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object.
        - path (:obj:`List[str]`): Path of the view.

    Returns:
        - tree (:obj:`_TreeValue`): Viewed tree value object.

    Example:
        >>> view(TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}), ['x'])  # TreeValue({'c': 3, 'd': 4})
    """
    return tree.__class__(get_data_property(tree).view(path))


def clone(tree: _TreeValue) -> _TreeValue:
    """
    Overview:
        Create a fully clone of the given tree.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object

    Returns:
        - tree (:obj:`_TreeValue`): Cloned tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> clone(t.x)  # TreeValue({'c': 3, 'd': 4})
    """
    return tree.__class__(get_data_property(tree).json())


def typetrans(tree: TreeValue, return_type: Type[_TreeValue]) -> _TreeValue:
    """
    Overview:
        Transform tree value object to another tree value type.

    Arguments:
        - tree (:obj:`TreeValue`): Tree value object
        - return_type (:obj:`Type[_TreeValue]`): Target tree value type

    Returns:
        - tree (:obj:`_TreeValue`): Transformed tree value object.

    Example:
        >>> t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> typetrans(t, TreeValue)  # TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    """
    if not issubclass(return_type, TreeValue):
        raise TypeError("Tree value should be subclass of TreeValue, but {type} found.".format(
            type=repr(return_type.__name__)
        ))

    return return_type(get_data_property(tree))


def mapping(tree: _TreeValue, func) -> _TreeValue:
    """
    Overview:
        Do mapping on every value in this tree.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:): Function for mapping

    Returns:
        - tree (:obj:`_TreeValue`): Mapped tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> mapping(t, lambda x: x + 2)  # TreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
    """
    from ..func import func_treelize
    return func_treelize(return_type=tree.__class__)(func)(tree)
