import pytest

from treevalue import TreeValue, flatten, unflatten, mapping, mask, filter_, reduce_, jsonify, clone, FastTreeValue, \
    walk, typetrans, union, subside, rise
from .test_tree_benchmark import _TREE_DATA, _TREE_4


def _mapping_func_1():
    return 1


def _mapping_func_2(x):
    return x


def _mapping_func_3(x, p):
    return p


def _filter_func_1():
    return True


def _filter_func_2(x):
    return x


def _filter_func_3(x, p):
    return p


# noinspection DuplicatedCode
@pytest.mark.benchmark(group='treevalue_utils')
class TestTreeUtilsBenchmark:
    def __setup_tree(self):
        return TreeValue(_TREE_DATA)

    def test_flatten(self, benchmark):
        benchmark(flatten, self.__setup_tree())

    def test_unflatten(self, benchmark):
        uf = flatten(self.__setup_tree())
        benchmark(unflatten, uf)

    @pytest.mark.parametrize('mapper', [_mapping_func_1, _mapping_func_2, _mapping_func_3])
    def test_mapping(self, benchmark, mapper):
        benchmark(mapping, self.__setup_tree(), mapper)

    def test_mask(self, benchmark):
        t = self.__setup_tree()
        mk = mapping(t, _filter_func_1)
        benchmark(mask, t, mk)

    @pytest.mark.parametrize('filterx', [_filter_func_1, _filter_func_2, _filter_func_3])
    def test_filter_(self, benchmark, filterx):
        benchmark(filter_, self.__setup_tree(), filterx)

    def test_reduce(self, benchmark):
        benchmark(reduce_, _TREE_4, lambda **kwargs: sum(kwargs.values()))

    def test_jsonify(self, benchmark):
        benchmark(jsonify, self.__setup_tree())

    def test_clone(self, benchmark):
        benchmark(clone, self.__setup_tree())

    def test_typetrans(self, benchmark):
        benchmark(typetrans, self.__setup_tree(), FastTreeValue)

    def test_walk(self, benchmark):
        benchmark(walk, self.__setup_tree())

    def test_walk_all(self, benchmark):
        def walk_all(t):
            for _ in walk(t):
                pass

        benchmark(walk_all, self.__setup_tree())

    @pytest.mark.parametrize('cnt', [2, 3, 4])
    def test_union(self, benchmark, cnt):
        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 5, 'b': 6, 'x': {'c': 7, 'd': 8}})
        t3 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t4 = TreeValue({'a': 5, 'b': 6, 'x': {'c': 7, 'd': 8}})

        trees = [t1, t2, t3, t4]
        benchmark(union, *trees[:cnt])

    def test_subside(self, benchmark):
        original1 = {
            'a': TreeValue({'a': 1, 'b': 2}),
            'x': {
                'c': TreeValue({'a': 3, 'b': 4}),
                'd': [
                    TreeValue({'a': 5, 'b': 6}),
                    TreeValue({'a': 7, 'b': 8}),
                ]
            },
            'k': '233'
        }
        benchmark(subside, original1)

    def test_rise(self, benchmark):
        original1 = {
            'a': TreeValue({'a': 1, 'b': 2}),
            'x': {
                'c': TreeValue({'a': 3, 'b': 4}),
                'd': [
                    TreeValue({'a': 5, 'b': 6}),
                    TreeValue({'a': 7, 'b': 8}),
                ]
            },
            'k': '233'
        }
        tk = subside(original1)
        benchmark(rise, tk)
