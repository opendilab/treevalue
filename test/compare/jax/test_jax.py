from functools import reduce

import jax.tree_util as pytree
import pytest

from treevalue import FastTreeValue, mapping, flatten, unflatten, flatten_values, flatten_keys

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)


@pytest.mark.benchmark(group='jax-pytree')
class TestCompareWithJaxPytree:
    def test_jax_tree_map(self, benchmark):
        benchmark(pytree.tree_map, lambda x: x ** 2, _TREE_DATA_1)

    def test_tv_mapping(self, benchmark):
        benchmark(mapping, _TREE_1, lambda x: x ** 2)

    def test_tv_mapping_with_path(self, benchmark):
        benchmark(mapping, _TREE_1, lambda x, p: x ** 2)

    def test_jax_tree_flatten(self, benchmark):
        benchmark(pytree.tree_flatten, _TREE_DATA_1)

    def test_tv_flatten(self, benchmark):
        benchmark(flatten, _TREE_1)

    def test_jax_tree_unflatten(self, benchmark):
        leaves, treedef = pytree.tree_flatten(_TREE_DATA_1)
        benchmark(pytree.tree_unflatten, treedef, leaves)

    def test_tv_unflatten(self, benchmark):
        flatted = flatten(_TREE_1)
        benchmark(unflatten, flatted)

    def test_jax_tree_all(self, benchmark):
        benchmark(pytree.tree_all, _TREE_DATA_1)

    def test_tv_flatten_all(self, benchmark):
        def _flatten_all(tree):
            return all(flatten_values(tree))

        benchmark(_flatten_all, _TREE_1)

    def test_jax_tree_leaves(self, benchmark):
        benchmark(pytree.tree_leaves, _TREE_DATA_1)

    def test_tv_flatten_values(self, benchmark):
        benchmark(flatten_values, _TREE_1)

    def test_jax_tree_reduce(self, benchmark):
        benchmark(pytree.tree_reduce, lambda x, y: x + y, _TREE_DATA_1)

    def test_jax_tree_reduce_with_init(self, benchmark):
        benchmark(pytree.tree_reduce, lambda x, y: x + y, _TREE_DATA_1, 0)

    def test_tv_flatten_reduce(self, benchmark):
        def _flatten_reduce(tree):
            values = flatten_values(tree)
            return reduce(lambda x, y: x + y, values)

        return benchmark(_flatten_reduce, _TREE_1)

    def test_tv_flatten_reduce_with_init(self, benchmark):
        def _flatten_reduce_with_init(tree):
            values = flatten_values(tree)
            return reduce(lambda x, y: x + y, values, 0)

        return benchmark(_flatten_reduce_with_init, _TREE_1)

    def test_jax_tree_structure(self, benchmark):
        benchmark(pytree.tree_structure, _TREE_DATA_1)

    def test_tv_flatten_keys(self, benchmark):
        benchmark(flatten_keys, _TREE_1)
