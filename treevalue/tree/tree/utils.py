from itertools import chain
from typing import TypeVar, List, Type, Tuple, Union, Any, Optional, Callable

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
    return tree.__class__(get_data_property(tree).clone())


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
        - `tree` (:obj:`_TreeValue`): Tree value object
        - `mask_` (:obj:`TreeValue`): Tree value mask object
        - `remove_empty` (:obj:`bool`): Remove empty tree node automatically, default is `True`.

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

    return subside(tuple(trees), inherit=inherit, return_type=return_type, **kwargs)


def subside(value, dict_: bool = True, list_: bool = True, tuple_: bool = True,
            return_type: Optional[Type[_TreeValue]] = None, inherit: bool = True, **kwargs) -> _TreeValue:
    """
    Overview:
        Drift down the structures (list, tuple, dict) down to the tree's value.

    Arguments:
        - value (:obj:): Original value object, may be nested dict, list or tuple.
        - `dict_` (:obj:`bool`): Enable dict subside, default is `True`.
        - `list_` (:obj:`bool`): Enable list subside, default is `True`.
        - `tuple_` (:obj:`bool`): Enable list subside, default is `True`.
        - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, \
            will be auto detected when there is exactly one tree value type in this original value, \
            otherwise the default will be `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `False`.
        - missing (:obj:): Missing value or lambda generator of when missing, default is `MISSING_NOT_ALLOW`, which \
            means raise `KeyError` when missing detected.

    Returns:
        - return (:obj:`_TreeValue`): Subsided tree value.

    Example:
        >>> data = {
        >>>     'a': TreeValue({'a': 1, 'b': 2}),
        >>>     'x': {
        >>>         'c': TreeValue({'a': 3, 'b': 4}),
        >>>         'd': [
        >>>             TreeValue({'a': 5, 'b': 6}),
        >>>             TreeValue({'a': 7, 'b': 8}),
        >>>         ]
        >>>     },
        >>>     'k': '233'
        >>> }
        >>>
        >>> tree = subside(data)
        >>> # tree should be --> TreeValue({
        >>> #    'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
        >>> #    'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        >>> #}), all structures above the tree values are subsided to the bottom of the tree.
    """

    def _build_func(v) -> Tuple[int, iter, Callable]:
        if dict_ and isinstance(v, dict):
            results = sorted([(key, _build_func(value_)) for key, value_ in v.items()])

            def _new_func(*args):
                position = 0
                returns = {}
                for key, (cnt, _, func) in results:
                    returns[key] = func(*args[position:position + cnt])
                    position += cnt

                return type(v)(returns)

            return sum([cnt for _, (cnt, _, _) in results]), chain(
                *[it for _, (_, it, _) in results]), _new_func
        elif (list_ and isinstance(v, list)) or (tuple_ and isinstance(v, tuple)):
            results = [_build_func(item) for item in v]

            def _new_func(*args):
                position = 0
                returns = []
                for cnt, _, func in results:
                    returns.append(func(*args[position: position + cnt]))
                    position += cnt

                return type(v)(returns)

            return sum([cnt for cnt, _, _ in results]), chain(
                *[it for _, it, _ in results]), _new_func

        else:
            return 1, (v,).__iter__(), lambda x: x

    def _get_default_type(args):
        types = {type(item) for item in args if isinstance(item, TreeValue)}
        if len(types) == 1:
            return list(types)[0]
        else:
            return None

    count, iter_, builder = _build_func(value)
    arguments = list(iter_)
    return_type = return_type or _get_default_type(arguments) or TreeValue

    assert count == len(arguments)

    from ..func import func_treelize
    return func_treelize(return_type=return_type, inherit=inherit, **kwargs)(builder)(*arguments)


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
                return typetrans(_result, tree.__class__)
            else:
                return _result
        else:
            return t

    return _recursion(tree)
