from typing import TypeVar, List, Type, Tuple, Union, Any

from .tree import TreeValue, get_data_property
from ...utils import dynamic_call

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


def _build_path_tree(tree: _TreeValue) -> _TreeValue:
    def _recursion(path, t: _TreeValue):
        if isinstance(t, tree.__class__):
            return tree.__class__({key: _recursion(path + [key], value) for key, value in t})
        else:
            return tuple(path)

    return _recursion([], tree)


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
    return func_treelize(return_type=tree.__class__)(lambda args: dynamic_call(func)(*args))(
        union(tree, _build_path_tree(tree)))


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
    return _filter_by_masked_tree(union(mask_, tree, return_type=tree.__class__), remove_empty)


def filter_(tree: _TreeValue, func, remove_empty: bool = True) -> _TreeValue:
    """
    Overview:
        Filter the element in the tree with a predict function.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:): Function for filtering
        - remove_empty (:obj:`bool`): Remove empty tree node automatically, default is `True`.

    Returns:
        - tree (:obj:`_TreeValue`): Filtered tree value object.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> filter_(t, lambda x: x < 3)         # TreeValue({'a': 1, 'b': 2})
        >>> filter_(t, lambda x: x < 3, False)  # TreeValue({'a': 1, 'b': 2, 'x': {}})
        >>> filter_(t, lambda x: x % 2 == 1)    # TreeValue({'a': 1, 'x': {'c': 3}})
    """
    return mask(tree, mapping(tree, func), remove_empty)


def union(*trees: TreeValue, return_type=None, inherit=True, **kwargs):
    """
    Overview:
        Union tree values together.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `False`.
        - missing (:obj:): Missing value or lambda generator of when missing, default is `MISSING_NOT_ALLOW`, which \
            means raise `KeyError` when missing detected.

    Returns:
        - result (:obj:`TreeValue`): Unionised tree value.

    Example:
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> tx = mapping(t, lambda v: v % 2 == 1)
        >>> union(t, tx)  # TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})
    """
    if return_type is None:
        return_type = trees[0].__class__ if trees else TreeValue

    from ..func import func_treelize
    return func_treelize(inherit=inherit, return_type=return_type, **kwargs)(lambda *args: tuple(args))(*trees)


def shrink(tree: _TreeValue, func):
    """
    Overview
        Shrink the tree to value.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:): Function for shrinking

    Returns:
        - result (:obj:): Shrunk result

    Examples:
        >>> from functools import reduce
        >>>
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> shrink(t, lambda **kwargs: sum(kwargs.values()))  # 10, 1 + 2 + (3 + 4)
        >>> shrink(t, lambda **kwargs: reduce(lambda x, y: x * y, list(kwargs.values())))  # 24, 1 * 2 * (3 * 4)
    """

    def _recursion(t: _TreeValue):
        if isinstance(t, tree.__class__):
            _result = func(**{key: _recursion(value) for key, value in t})
            if isinstance(_result, TreeValue):
                return tree.__class__(_result)
            else:
                return _result
        else:
            return t

    return _recursion(tree)
