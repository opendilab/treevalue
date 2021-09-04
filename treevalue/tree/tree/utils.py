from functools import partial
from itertools import chain
from typing import TypeVar, List, Type, Tuple, Union, Any, Optional, Callable

from .tree import TreeValue, get_data_property
from ..common import raw
from ...utils import dynamic_call, common_direct_base, SingletonMark

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


def clone(tree: _TreeValue, copy_value: Union[None, bool, Callable, Any] = None) -> _TreeValue:
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
    return tree.__class__(get_data_property(tree).clone(copy_value))


def typetrans(tree: TreeValue, return_type: Type[_TreeValue]) -> _TreeValue:
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


def mapping(tree: _TreeValue, func: Callable) -> _TreeValue:
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


def filter_(tree: _TreeValue, func: Callable, remove_empty: bool = True) -> _TreeValue:
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
    return mask(tree, mapping(tree, func), remove_empty)


def union(*trees: TreeValue, return_type=None, **kwargs):
    """
    Overview:
        Union tree values together.

    Arguments:
        - trees (:obj:`_TreeValue`): Tree value objects.
        - mode (:obj:): Mode of the wrapping (string or TreeMode both okay), default is `strict`.
        - return_type (:obj:`Optional[Type[_ClassType]]`): Return type of the wrapped function, default is `TreeValue`.
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
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

    return subside(tuple(trees), return_type=return_type, **kwargs)


def subside(value, dict_: bool = True, list_: bool = True, tuple_: bool = True,
            return_type: Optional[Type[_TreeValue]] = None, **kwargs) -> _TreeValue:
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
        - inherit (:obj:`bool`): Allow inherit in wrapped function, default is `True`.
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
        try:
            return common_direct_base(*list(types))
        except TypeError:
            return None

    count, iter_, builder = _build_func(value)
    arguments = list(iter_)
    return_type = return_type or _get_default_type(arguments) or TreeValue
    assert count == len(arguments)

    from ..func import func_treelize
    return func_treelize(return_type=return_type, **kwargs)(builder)(*arguments)


#: Means no template is given to the rise function, \
#: and the decorated function will automatically \
#: try to match the format patterns as template.
NO_RISE_TEMPLATE = SingletonMark("no_rise_template")


def rise(tree: _TreeValue, dict_: bool = True, list_: bool = True, tuple_: bool = True,
         template=NO_RISE_TEMPLATE):
    """
    Overview:
        Make the structure (dict, list, tuple) in value rise up to the top, above the tree value.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - `dict_` (:obj:`bool`): Enable dict rise, default is `True`.
        - `list_` (:obj:`bool`): Enable list rise, default is `True`.
        - `tuple_` (:obj:`bool`): Enable list rise, default is `True`.
        - template (:obj:): Rising template, default is `NO_RISE_TEMPLATE`, which means auto detect.

    Returns:
        - risen (:obj:): Risen value.

    Example:
        >>> t = TreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6, 7], 'b': [7, 8]})})
        >>> dt = rise(t)
        >>> # dt will be {'a': <TreeValue 1>, 'b': [<TreeValue 2>, <TreeValue 3>]}
        >>> # TreeValue 1 will be TreeValue({'x': [1, 2], 'y': [5, 6, 7]})
        >>> # TreeValue 2 will be TreeValue({'x': 2, 'y': 7})
        >>> # TreeValue 3 will be TreeValue({'x': 3, 'y': 8})
        >>>
        >>> t2 = TreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6], 'b': [7, 8]})})
        >>> dt2 = rise(t2)
        >>> # dt2 will be {'a': [<TreeValue 1>, <TreeValue 2>], 'b': [<TreeValue 3>, <TreeValue 4>]}
        >>> # TreeValue 1 will be TreeValue({'x': 1, 'y': 5})
        >>> # TreeValue 2 will be TreeValue({'x': 2, 'y': 6})
        >>> # TreeValue 3 will be TreeValue({'x': 2, 'y': 7})
        >>> # TreeValue 4 will be TreeValue({'x': 3, 'y': 8})
        >>>
        >>> dt3 = rise(t2, template={'a': None, 'b': None})
        >>> # dt3 will be {'a': <TreeValue 1>, 'b': <TreeValue 2>}
        >>> # TreeValue 1 will be TreeValue({'x': [1, 2], 'y': [5, 6]})
        >>> # TreeValue 2 will be TreeValue({'x': [2, 3], 'y': [7, 8]})
    """

    def _get_tree_builder(t: _TreeValue):
        if isinstance(t, TreeValue):
            results = sorted([(key, _get_tree_builder(value)) for key, value in t])

            def _new_func(*args):
                position = 0
                returns = {}
                for key, (cnt, _, func_) in results:
                    returns[key] = func_(*args[position:position + cnt])
                    position += cnt

                return tree.__class__(returns)

            return sum([cnt for _, (cnt, _, _) in results]), chain(
                *[iter_ for _, (_, iter_, _) in results]), _new_func

        else:
            return 1, (t,).__iter__(), lambda x: raw(x)

    def _get_common_structure_getter(*args, tpl=NO_RISE_TEMPLATE):
        if not args:
            return 0, [], lambda: clone(tree)

        types = [type(item) for item in args]
        if tpl is not NO_RISE_TEMPLATE:
            types.append(type(tpl))
        base_class = common_direct_base(*types)
        if dict_ and issubclass(base_class, dict):
            keysets = [tuple(sorted(item.keys())) for item in args]
            if len(set(keysets)) == 1:
                keyset = sorted(list(keysets)[0])
                results = [(key, _get_common_structure_getter(
                    *[item[key] for item in args],
                    tpl=NO_RISE_TEMPLATE if tpl is NO_RISE_TEMPLATE else tpl[key]
                )) for key in keyset]
                getter_lists = {key: getters for key, (_, getters, _) in results}

                def _new_func(*args_):
                    position = 0
                    result = {}
                    for key, (cnt, _, func) in results:
                        result[key] = func(*args_[position:position + cnt])
                        position += cnt

                    return base_class(result)

                return sum([cnt for _, (cnt, _, _) in results]), [
                    partial(lambda k, g, x: g(x[k]), key, getter)
                    for key in keyset for getter in getter_lists[key]], _new_func

        elif (list_ and issubclass(base_class, list)) or \
                (tuple_ and issubclass(base_class, tuple)):
            if issubclass(base_class, list):
                if tpl is not NO_RISE_TEMPLATE:
                    if len(tpl) > 1:
                        raise ValueError("Length of list template should be no more than 1, "
                                         f"but {len(tpl)} found.")
                    _inner_tpl = tpl[0] if len(tpl) > 0 else None
                else:
                    _inner_tpl = NO_RISE_TEMPLATE
                _inner_tpl_getter = lambda index: _inner_tpl
            else:
                _inner_tpl_getter = lambda index: (NO_RISE_TEMPLATE if tpl is NO_RISE_TEMPLATE else tpl[index])

            lengths = [len(item) for item in args]
            if len(set(lengths)) == 1:
                length = list(lengths)[0]
                results = [_get_common_structure_getter(
                    *[item[i] for item in args], tpl=_inner_tpl_getter(i)
                ) for i in range(length)]
                getter_lists = [getters for _, getters, _ in results]

                def _new_func(*args_):
                    position = 0
                    result = []
                    for cnt, _, func in results:
                        result.append(func(*args_[position: position + cnt]))
                        position += cnt

                    return base_class(result)

                return sum([cnt for cnt, _, _ in results]), [
                    partial(lambda i, g, x: g(x[i]), index, getter)
                    for index in range(length) for getter in getter_lists[index]], _new_func

        if tpl is not NO_RISE_TEMPLATE and ((dict_ and isinstance(tpl, dict)) or (
                list_ and isinstance(tpl, list)) or (tuple_ and isinstance(tpl, tuple))):
            raise ValueError("Template not able to be applied "
                             "for schema {tpl} expected but not match is some values.".format(tpl=repr(tpl)))

        return 1, [lambda x: x], (lambda x: x)

    value_count, value_iter, tree_builder = _get_tree_builder(tree)
    value_list = list(value_iter)
    assert value_count == len(value_list)

    meta_value_count, meta_value_getters, value_builder = _get_common_structure_getter(*value_list, tpl=template)
    assert meta_value_count == len(meta_value_getters)

    return value_builder(*map(lambda getter_: tree_builder(*map(getter_, value_list)), meta_value_getters))


def reduce_(tree: _TreeValue, func):
    """
    Overview
        Reduce the tree to value.

    Arguments:
        - tree (:obj:`_TreeValue`): Tree value object
        - func (:obj:): Function for reducing

    Returns:
        - result (:obj:): Reduce result

    Examples:
        >>> from functools import reduce
        >>>
        >>> t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        >>> reduce_(t, lambda **kwargs: sum(kwargs.values()))  # 10, 1 + 2 + (3 + 4)
        >>> reduce_(t, lambda **kwargs: reduce(lambda x, y: x * y, list(kwargs.values())))  # 24, 1 * 2 * (3 * 4)
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
