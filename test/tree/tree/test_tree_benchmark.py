from functools import lru_cache
from operator import __eq__

import pytest

from treevalue import TreeValue, raw, to_constraint
from .test_constraint import GreaterThanConstraint

_TREE_DATA = {'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}}
_TREE = TreeValue(_TREE_DATA)
_TREE_CONSTRAINT = [GreaterThanConstraint(0), {'a': int, 'b': int, 'c': dict, 'd': {'x': int, 'y': int}}]

_TREE_DATA_2 = {'e': 3, 'f': 'klsjdfgklsdf', 'g': raw({'x': 3, 'y': 4}), 'c': {'x': 3, 'y': 4}}
_TREE_2 = TreeValue(_TREE_DATA_2)

_TREE_DATA_3 = {}
_TREE_3 = TreeValue(_TREE_DATA_3)

_TREE_DATA_4 = {'a': 1, 'b': 2, 'd': {'x': 3, 'y': 4}}
_TREE_4 = TreeValue(_TREE_DATA_4)


# need to warm up when first run this
# because some features (e.g. child tree's constraint) will use cache
@pytest.mark.benchmark(group='treevalue_class', warmup=True, min_rounds=20)
class TestTreeValueBenchmark:
    @lru_cache()
    def __setup_tree(self):
        return TreeValue(_TREE_DATA)

    @lru_cache()
    def __setup_constraint_tree(self):
        return TreeValue(_TREE_DATA, constraint=_TREE_CONSTRAINT)

    @pytest.mark.parametrize('data', [_TREE_DATA])
    def test_init(self, benchmark, data):
        result = benchmark(TreeValue, data)
        assert result == _TREE

    @pytest.mark.parametrize('data, constraint', [(_TREE_DATA, _TREE_CONSTRAINT),
                                                  (_TREE_DATA, to_constraint(_TREE_CONSTRAINT))])
    def test_init_constraint(self, benchmark, data, constraint):
        result = benchmark(TreeValue, data, constraint)
        assert result == _TREE
        assert result.constraint == constraint

    def test_detach(self, benchmark):
        benchmark(TreeValue._detach, self.__setup_tree())

    @pytest.mark.parametrize('args', [('a',), ('a', 1), ('d',), ('f', 1)])
    def test_get(self, benchmark, args):
        benchmark(TreeValue.get, self.__setup_tree(), *args)

    @pytest.mark.parametrize('args', [('a',), ('a', 1), ('d',), ('f', 1)])
    def test_get_constraint(self, benchmark, args):
        benchmark(TreeValue.get, self.__setup_constraint_tree(), *args)

    @pytest.mark.parametrize('key', ['a', 'd'])
    def test_getattr(self, benchmark, key):
        benchmark(getattr, self.__setup_tree(), key)

    @pytest.mark.parametrize('key', ['a', 'd'])
    def test_getattr_constraint(self, benchmark, key):
        benchmark(getattr, self.__setup_constraint_tree(), key)

    @pytest.mark.parametrize('key, data', [('a', 1), ('e', 233)])
    def test_setattr(self, benchmark, key, data):
        benchmark(setattr, self.__setup_tree(), key, data)

    @pytest.mark.parametrize('key', ['a'])
    def test_delattr_after_setattr(self, benchmark, key):
        def set_and_del(t: TreeValue, k: str):
            setattr(t, k, 1)
            delattr(t, k)

        benchmark(set_and_del, self.__setup_tree(), key)

    @pytest.mark.parametrize('key', ['a', 'e'])
    def test_contains(self, benchmark, key):
        benchmark(TreeValue.__contains__, self.__setup_tree(), key)

    def test_len(self, benchmark):
        benchmark(len, self.__setup_tree())

    @pytest.mark.parametrize('tree', [_TREE, _TREE_3])
    def test_bool(self, benchmark, tree):
        benchmark(bool, tree)

    @pytest.mark.parametrize('tree', [_TREE, _TREE_3])
    def test_repr(self, benchmark, tree):
        benchmark(repr, tree)

    @pytest.mark.parametrize('tree', [_TREE_4, _TREE_3])
    def test_hash(self, benchmark, tree):
        benchmark(hash, tree)

    @pytest.mark.parametrize('tree', [_TREE, _TREE_2])
    def test_eq(self, benchmark, tree):
        benchmark(__eq__, self.__setup_tree(), tree)
