try:
    import nest
except ImportError:
    nest = None
import pytest

from treevalue import FastTreeValue, flatten, mapping, func_treelize, unflatten, union

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)

_UMARK = pytest.mark.benchmark(group='facebook-nest') if nest is not None else pytest.mark.ignore


@_UMARK
class TestCompareFacebookNest:
    N = 5

    def __create_nested_tree_data(self, n):
        return {
            ('no_%04d' % (i + 1,)): _TREE_DATA_1 for i in range(n)
        }

    def __create_nested_tree(self, n):
        return FastTreeValue(self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_nest_flatten(self, benchmark, n):
        benchmark(nest.flatten, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_flatten(self, benchmark, n):
        benchmark(flatten, self.__create_nested_tree(n))

    def test_nest_pack_as(self, benchmark):
        benchmark(nest.pack_as, _TREE_DATA_1, nest.flatten(_TREE_DATA_1))

    def test_tv_unflatten(self, benchmark):
        benchmark(unflatten, flatten(_TREE_1))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_nest_map(self, benchmark, n):
        benchmark(nest.map, lambda x: x ** 2, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_map(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree(n), lambda x: x ** 2)

    def test_nest_map_many2(self, benchmark):
        def f(a, b):
            return a ** b + a * b

        benchmark(nest.map_many2, f, _TREE_DATA_1, _TREE_DATA_1)

    def test_nest_map_many(self, benchmark):
        def f(a):
            return a[0] ** a[1] + a[0] * a[1]

        benchmark(nest.map_many, f, _TREE_DATA_1, _TREE_DATA_1)

    def test_tv_treelize_call(self, benchmark):
        @func_treelize()
        def f(a, b):
            return a ** b + a * b

        benchmark(f, _TREE_1, _TREE_1)

    def test_tv_mapping_union(self, benchmark):
        def f(a):
            return a[0] ** a[1]

        def _my_func(fx, *v):
            return mapping(union(*v), fx)

        benchmark(_my_func, f, _TREE_1, _TREE_1)
