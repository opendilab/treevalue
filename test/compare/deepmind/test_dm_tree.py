import pytest
import tree  # dm-tree https://github.com/deepmind/tree

from treevalue import FastTreeValue, flatten, mapping

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)


@pytest.mark.benchmark(group='dm-tree')
class TestCompareWithDMTree:
    def test_dm_flatten_with_path(self, benchmark):
        benchmark(tree.flatten_with_path, _TREE_DATA_1)

    def test_dm_flatten_without_path(self, benchmark):
        benchmark(tree.flatten, _TREE_DATA_1)

    def test_tv_flatten(self, benchmark):
        benchmark(flatten, _TREE_1)

    def test_dm_map_structure(self, benchmark):
        benchmark(tree.map_structure, lambda x: x ** 2, _TREE_DATA_1)

    def test_tv_mapping(self, benchmark):
        benchmark(mapping, _TREE_1, lambda x: x ** 2)

    def test_dm_map_structure_with_path(self, benchmark):
        benchmark(tree.map_structure_with_path, lambda p, x: x * len(p), _TREE_DATA_1)

    def test_tv_mapping_with_path(self, benchmark):
        benchmark(mapping, _TREE_1, lambda x, p: x * len(p))
