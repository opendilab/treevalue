from functools import reduce

import jax.tree_util as pytree
import pytest

from treevalue import FastTreeValue, mapping, flatten, unflatten, flatten_values, flatten_keys, subside, rise, raw

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)


@pytest.mark.benchmark(group='jax-pytree')
class TestCompareWithJaxPytree:
    N = 5

    def __create_nested_tree_data(self, n):
        return {
            ('no_%04d' % (i + 1,)): _TREE_DATA_1 for i in range(n)
        }

    def __create_nested_tree(self, n):
        return FastTreeValue(self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_jax_tree_map(self, benchmark, n):
        benchmark(pytree.tree_map, lambda x: x ** 2, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree(n), lambda x: x ** 2)

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping_with_path(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree(n), lambda x, p: x ** 2)

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_jax_tree_flatten(self, benchmark, n):
        benchmark(pytree.tree_flatten, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_flatten(self, benchmark, n):
        benchmark(flatten, self.__create_nested_tree(n))

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

    def test_jax_tree_transpose(self, benchmark):
        sto = pytree.tree_structure({'a': 1, 'b': 2, 'c': {'x': 3, 'y': 4}})
        sti = pytree.tree_structure({'a': 1, 'b': {'x': 2, 'y': 3}})

        value = (
            {'a': 1, 'b': {'x': 2, 'y': 3}},
            {
                'a': {'a': 10, 'b': {'x': 20, 'y': 30}},
                'b': [
                    {'a': 100, 'b': {'x': 200, 'y': 300}},
                    {'a': 400, 'b': {'x': 500, 'y': 600}},
                ],
            }
        )
        benchmark(pytree.tree_transpose, sto, sti, value)

    def test_tv_subside(self, benchmark):
        value = {
            'a': FastTreeValue({'a': 1, 'b': {'x': 2, 'y': 3}}),
            'b': FastTreeValue({'a': 10, 'b': {'x': 20, 'y': 30}}),
            'c': {
                'x': FastTreeValue({'a': 100, 'b': {'x': 200, 'y': 300}}),
                'y': FastTreeValue({'a': 400, 'b': {'x': 500, 'y': 600}}),
            },
        }
        benchmark(subside, value)

    def test_tv_rise(self, benchmark):
        value = FastTreeValue({
            'a': raw({'a': 1, 'b': {'x': 2, 'y': 3}}),
            'b': raw({'a': 10, 'b': {'x': 20, 'y': 30}}),
            'c': {
                'x': raw({'a': 100, 'b': {'x': 200, 'y': 300}}),
                'y': raw({'a': 400, 'b': {'x': 500, 'y': 600}}),
            },
        })
        benchmark(rise, value)

    def test_tv_rise_with_template(self, benchmark):
        value = FastTreeValue({
            'a': raw({'a': 1, 'b': {'x': 2, 'y': 3}}),
            'b': raw({'a': 10, 'b': {'x': 20, 'y': 30}}),
            'c': {
                'x': raw({'a': 100, 'b': {'x': 200, 'y': 300}}),
                'y': raw({'a': 400, 'b': {'x': 500, 'y': 600}}),
            },
        })
        benchmark(rise, value, template={'a': None, 'b': {'x': None, 'y': None}})
