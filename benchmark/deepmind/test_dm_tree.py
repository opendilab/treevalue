from unittest import skipUnless

import pytest
import torch
import tree  # dm-tree https://github.com/deepmind/tree
from hbutils.collection import nested_map

from treevalue import FastTreeValue, flatten, mapping
from ..base import CMP_N, HAS_CUDA

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)

_TREE_DATA_2 = {'obs': torch.randn(4, 84, 84), 'action': torch.randint(0, 6, size=(1,)), 'reward': torch.rand(1)}
_TREE_2 = FastTreeValue(_TREE_DATA_2)

if HAS_CUDA:
    _TREE_DATA_2_CUDA = nested_map(lambda x: x.cuda(), _TREE_DATA_2)


@pytest.mark.benchmark(group='dm-tree')
class TestCompareWithDMTree:
    N = CMP_N

    def __create_nested_tree_data(self, n):
        return {
            ('no_%04d' % (i + 1,)): _TREE_DATA_1 for i in range(n)
        }

    def __create_nested_tree_data_torch(self, n, cuda: bool = False):
        return {
            ('no_%04d' % (i + 1,)): (_TREE_DATA_2 if not cuda else _TREE_DATA_2_CUDA) for i in range(n)
        }

    def __create_nested_tree(self, n):
        return FastTreeValue(self.__create_nested_tree_data(n))

    def __create_nested_tree_torch(self, n, cuda: bool = False):
        return FastTreeValue(self.__create_nested_tree_data_torch(n, cuda))

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

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_map_structure_torch(self, benchmark, n):
        benchmark(tree.map_structure, lambda x: x ** 2, self.__create_nested_tree_data_torch(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping_torch(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree_torch(n), lambda x: x ** 2)

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_dm_map_structure_with_path_torch(self, benchmark, n):
        benchmark(tree.map_structure_with_path, lambda p, x: x * len(p), self.__create_nested_tree_data_torch(n))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    def test_tv_mapping_with_path_torch(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree_torch(n), lambda x, p: x * len(p))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_dm_map_structure_torch_cuda(self, benchmark, n):
        benchmark(tree.map_structure, lambda x: x ** 2, self.__create_nested_tree_data_torch(n, cuda=True))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tv_mapping_torch_cuda(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree_torch(n, cuda=True), lambda x: x ** 2)

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_dm_map_structure_with_path_torch_cuda(self, benchmark, n):
        benchmark(tree.map_structure_with_path, lambda p, x: x * len(p),
                  self.__create_nested_tree_data_torch(n, cuda=True))

    @pytest.mark.parametrize('n', [2 ** i for i in range(N)])
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tv_mapping_with_path_torch_cuda(self, benchmark, n):
        benchmark(mapping, self.__create_nested_tree_torch(n, cuda=True), lambda x, p: x * len(p))
