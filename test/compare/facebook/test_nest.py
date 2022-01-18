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
    def test_nest_flatten(self, benchmark):
        benchmark(nest.flatten, _TREE_DATA_1)

    def test_tv_flatten(self, benchmark):
        benchmark(flatten, _TREE_1)

    def test_nest_pack_as(self, benchmark):
        benchmark(nest.pack_as, _TREE_DATA_1, nest.flatten(_TREE_DATA_1))

    def test_tv_unflatten(self, benchmark):
        benchmark(unflatten, flatten(_TREE_1))

    def test_nest_map(self, benchmark):
        benchmark(nest.map, lambda x: x ** 2, _TREE_DATA_1)

    def test_tv_map(self, benchmark):
        benchmark(mapping, _TREE_1, lambda x: x ** 2)

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
