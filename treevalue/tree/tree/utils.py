from typing import TypeVar, List, Type, Tuple, Union, Any

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


def _filter_by_masked_tree(masked_tree: _TreeValue, remove_empty: bool) -> _TreeValue:
    def _recursion(t: Union[_TreeValue, Any]) -> Tuple[bool, _TreeValue]:
        if isinstance(t, masked_tree.__class__):
            dict_result = {key: _recursion(value) for key, value in t}
            dict_result = {key: value for key, (flag, value) in dict_result.items() if flag}
            result = masked_tree.__class__(dict_result)

            return not not result if remove_empty else True, result
        else:
            return t

    _, _result = _recursion(masked_tree)
    return _result


def mask(tree: _TreeValue, mask_: Union[TreeValue, bool], remove_empty: bool = True) -> _TreeValue:
    """
    Overview:
        Filter the element in the tree with a mask

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - mask_ (:obj:`TreeValue`): Tree value mask object
        - remove_empty (:obj:`bool`): Remove empty tree node automatically, default is `True`.

    Returns:
        - tree (:obj:`_TreeValue`): Filtered tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> mask(t, TreeValue({'a': True, 'b': False, 'x': False}))                    # TreeValue({'a': 1})
        >>> mask(t, TreeValue({'a': True, 'b': False, 'x': {'c': True, 'd': False}}))  # TreeValue({'a': 1, 'x': {'c': 3}})
    """
    from ..func import func_treelize
    raw_result = func_treelize(inherit=True, return_type=tree.__class__)(
        lambda t, f: (not not f, t))(tree, mask_)
    return _filter_by_masked_tree(raw_result, remove_empty)


def filter_(tree: _TreeValue, func, remove_empty: bool = True) -> _TreeValue:
    """
    Overview:
        Filter the element in the tree with a predict function.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - remove_empty (:obj:`bool`): Remove empty tree node automatically, default is `True`.

    Returns:
        - tree (:obj:`_TreeValue`): Filtered tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> filter_(t, lambda x: x < 3)         # TreeValue({'a': 1, 'b': 2})
        >>> filter_(t, lambda x: x < 3, False)  # TreeValue({'a': 1, 'b': 2, 'x': {}})
        >>> filter_(t, lambda x: x % 2 == 1)    # TreeValue({'a': 1, 'x': {'c': 3}})
    """
    raw_result = mapping(tree, lambda x: (not not func(x), x))
    return _filter_by_masked_tree(raw_result, remove_empty)
