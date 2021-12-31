import pytest
import tree  # dm-tree https://github.com/deepmind/tree

from treevalue import FastTreeValue, flatten, mapping

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)


@pytest.mark.benchmark(group='dm-tree')
class TestCompareWithDMTree:
    N = 5

    def __create_nested_tree_data(self, n):
        return {
            ('no_%04d' % (i + 1,)): _TREE_DATA_1 for i in range(n)
        }

    def __create_nested_tree(self, n):
        return FastTreeValue(self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_flatten_with_path(self, benchmark, n):
        benchmark(tree.flatten_with_path, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_flatten_without_path(self, benchmark, n):
        benchmark(tree.flatten, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_flatten(self, benchmark, n):
        benchmark(flatten, self.__create_nested_tree(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_map_structure(self, benchmark, n):
        benchmark(tree.map_structure, lambda x: x ** 2, self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree(n), lambda x: x ** 2)

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_map_structure_with_path(self, benchmark, n):
        benchmark(tree.map_structure_with_path, lambda p, x: x * len(p), self.__create_nested_tree_data(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping_with_path(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree(n), lambda x, p: x * len(p))
