import re
from copy import deepcopy
from functools import wraps
from typing import Dict, Any, Union, List, Callable

from .base import BaseTree
from ...utils import init_magic


class _RawWrapped:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value


_RAW_NEEDED_TYPES = (dict,)


def raw(value) -> _RawWrapped:
    """
    Overview:
        Wrap raw value to init tree or set item, can be used for dict.
        Can only performs when value is a dict object, otherwise just return the original value.

    Arguments:
        - value (:obj:): Original value.

    Returns:
        - wrapped (:obj:`_RawWrapped`): Wrapped value.

    Example:
        >>> t = Tree({
        >>>     'a': raw({'a': 1, 'b': 2}),
        >>>     'b': raw({'a': 3, 'b': 4}),
        >>>     'x': {
        >>>         'c': raw({'a': 5, 'b': 6}),
        >>>         'd': raw({'a': 7, 'b': 8}),
        >>>     }
        >>> })
        >>>
        >>> t['a']  # {'a': 1, 'b': 2}
        >>> t['b']  # {'a': 3, 'b': 4}
        >>> t['x']['c']  # {'a': 5, 'b': 6}
        >>> t['x']['d']  # {'a': 7, 'b': 8}
        >>>
        >>> t['a'] = raw({'a': 9, 'b': 10})
        >>> t['a']  # {'a': 9, 'b': 10}
        >>> t['a'] = {'a': 9, 'b': 10}
        >>> t['a']  # should be a Tree object when raw not used
    """
    if not isinstance(value, _RawWrapped) and isinstance(value, _RAW_NEEDED_TYPES):
        return _RawWrapped(value)
    else:
        return value


def _unraw(value):
    if isinstance(value, _RawWrapped):
        return value.value
    else:
        return value


_KEY_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,65534}$')


def _check_key(key):
    if not isinstance(key, str) or not _KEY_PATTERN.fullmatch(key):
        raise KeyError("Tree's key should be an ascii string matching regex of {regexp}, "
                       "but {key} found.".format(regexp=repr(_KEY_PATTERN.pattern), key=repr(key)))
    return key


def _to_tree_decorator(init_func):
    @wraps(init_func)
    def _new_init_func(data):
        if isinstance(data, BaseTree):
            _new_init_func(_tree_dump(data))
        elif isinstance(data, dict):
            init_func({
                _check_key(key): Tree(value) if isinstance(value, dict) else _unraw(value)
                for key, value in data.items()
            })
        else:
            raise TypeError(
                "Dict value expected for dispatch value but {type} actually.".format(type=repr(type(data).__name__)))

    return _new_init_func


def _copy_func(copy):
    if hasattr(copy, '__call__'):
        return copy
    elif copy is None or isinstance(copy, (bool,)):
        return (lambda x: deepcopy(x)) if copy else (lambda x: x)
    elif isinstance(copy, (list, tuple)):
        dumper, loader = copy[:2]
        return lambda x: loader(dumper(x))
    else:
        dumper, loader = getattr(copy, 'dumps'), getattr(copy, 'loads')
        return lambda x: loader(dumper(x))


def _tree_dump(tree: 'BaseTree', copy_value: Union[None, bool, Callable] = None):
    copy_value = _copy_func(copy_value)

    def _recursion(t):
        if isinstance(t, BaseTree):
            return {key: _recursion(value) for key, value in t.items()}
        else:
            return raw(copy_value(t))

    return _recursion(tree.actual())


@init_magic(_to_tree_decorator)
class Tree(BaseTree):
    """
    Overview:
        Tree node data model, based on `BaseTree`.
    """

    def __init__(self, data: Union[Dict[str, Union['Tree', Any]], 'Tree']):
        """
        Overview:
            Constructor of `Tree`, can be `dict`, `Tree`, `TreeView`.
            When dict passed in, a new tree structure will be created once.
            When `Tree` or `TreeView` passed in, a fully copy will be constructed in this object.

        Arguments:
            - data (:obj:`Union[Dict[str, Union['Tree', Any]], 'Tree']`): Any data can be parsed into `Tree`.

        Example:
            >>> t = Tree({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})  # t is a new tree structure
            >>> t2 = Tree(t)                                       # t2 is a full copy of t1
            >>> t3 = Tree({'a': t, 'b': t2})                       # t3 is a tree with subtree of t and t2 (not copy)
        """
        self.__dict = data

    def __check_key_exist(self, key):
        if key not in self.__dict.keys():
            raise KeyError("Key {key} not found.".format(key=repr(key)))

    def __getitem__(self, key):
        self.__check_key_exist(key)
        return self.__dict[key]

    def __setitem__(self, key, value):
        key = _check_key(key)
        if isinstance(value, dict):
            value = Tree(value)
        self.__dict[key] = _unraw(value)

    def __delitem__(self, key):
        self.__check_key_exist(key)
        del self.__dict[key]

    def view(self, path: List[str]):
        from .view import TreeView
        return TreeView(self, path)

    def clone(self, copy_value: Union[None, bool, Callable, Any] = None):
        return self.__class__(_tree_dump(self, copy_value))

    def copy_from(self, other: 'BaseTree'):
        other = other.actual()
        all_keys = sorted(set(other.keys()) | set(self.keys()))
        for key in all_keys:
            if key not in other.keys():
                del self[key]
            else:
                if isinstance(other[key], BaseTree):
                    if key in self.keys() and isinstance(self[key], BaseTree):
                        self[key].actual().copy_from(other[key].actual())
                    else:
                        self[key] = other[key].clone()
                else:
                    self[key] = other[key]

        return self

    def items(self):
        return self.__dict.items()

    def keys(self):
        return self.__dict.keys()

    def values(self):
        return self.__dict.values()

    def actual(self) -> 'Tree':
        return self

    def __getstate__(self):
        return {key: value.actual() if isinstance(value, BaseTree) else value
                for key, value in self.__dict.items()}

    def __setstate__(self, state):
        self.__dict = state
