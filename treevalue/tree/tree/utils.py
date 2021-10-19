from functools import partial
from itertools import chain
from typing import TypeVar, Type

from .service import clone
from .tree import TreeValue
from ..common import raw
from ...utils import common_direct_base, SingletonMark

_TreeValue = TypeVar("_TreeValue", bound=TreeValue)

#: Means no template is given to the rise function, \
#: and the decorated function will automatically \
#: try to match the format patterns as template.
NO_RISE_TEMPLATE = SingletonMark("no_rise_template")


def _rise_builder_new_func(*args, results, tv):
    position = 0
    returns = {}
    for key, (cnt, _, func_) in results:
        returns[key] = func_(*args[position:position + cnt])
        position += cnt

    return tv(returns)


def _rise_get_tree_builder(t: _TreeValue, tv: Type[TreeValue]):
    if isinstance(t, TreeValue):
        results = sorted([(key, _rise_get_tree_builder(value, tv)) for key, value in t])
        return sum([cnt for _, (cnt, _, _) in results]), \
               chain(*[iter_ for _, (_, iter_, _) in results]), \
               partial(_rise_builder_new_func, results=results, tv=tv)
    else:
        return 1, (t,).__iter__(), raw


def _rise_struct_dict_new_func(*args_, results, base_class):
    position = 0
    result = {}
    for key, (cnt, _, func) in results:
        result[key] = func(*args_[position:position + cnt])
        position += cnt

    return base_class(result)


def _rise_struct_list_new_func(*args_, results, base_class):
    position = 0
    result = []
    for cnt, _, func in results:
        result.append(func(*args_[position: position + cnt]))
        position += cnt

    return base_class(result)


def _get_common_structure_getter(*args, tpl=NO_RISE_TEMPLATE, tree, dict_: bool, list_: bool, tuple_: bool):
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
                tpl=NO_RISE_TEMPLATE if tpl is NO_RISE_TEMPLATE else tpl[key],
                tree=tree, dict_=dict_, list_=list_, tuple_=tuple_,
            )) for key in keyset]
            getter_lists = {key: getters for key, (_, getters, _) in results}

            return sum([cnt for _, (cnt, _, _) in results]), \
                   [partial(lambda k, g, x: g(x[k]), key, getter) for key in keyset for getter in
                    getter_lists[key]], \
                   partial(_rise_struct_dict_new_func, results=results, base_class=base_class)

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
                *[item[i] for item in args], tpl=_inner_tpl_getter(i),
                tree=tree, dict_=dict_, list_=list_, tuple_=tuple_,
            ) for i in range(length)]
            getter_lists = [getters for _, getters, _ in results]

            return sum([cnt for cnt, _, _ in results]), \
                   [partial(lambda i, g, x: g(x[i]), index, getter) for index in range(length) for getter in
                    getter_lists[index]], \
                   partial(_rise_struct_list_new_func, results=results, base_class=base_class)

    if tpl is not NO_RISE_TEMPLATE and ((dict_ and isinstance(tpl, dict)) or (
            list_ and isinstance(tpl, list)) or (tuple_ and isinstance(tpl, tuple))):
        raise ValueError("Template not able to be applied "
                         "for schema {tpl} expected but not match is some values.".format(tpl=repr(tpl)))

    return 1, [lambda x: x], (lambda x: x)


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

    tv = type(tree)

    value_count, value_iter, tree_builder = _rise_get_tree_builder(tree, tv)
    value_list = list(value_iter)
    assert value_count == len(value_list)

    meta_value_count, meta_value_getters, value_builder = \
        _get_common_structure_getter(*value_list, tpl=template,
                                     tree=tree, dict_=dict_, list_=list_, tuple_=tuple_)
    assert meta_value_count == len(meta_value_getters)

    return value_builder(*map(lambda getter_: tree_builder(*map(getter_, value_list)), meta_value_getters))
