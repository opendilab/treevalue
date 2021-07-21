from typing import TypeVar, List

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
