import copy
from unittest import skipUnless

import pytest
import torch
from hbutils.collection import nested_map
from tianshou.data import Batch  # tianshou Batch https://tianshou.readthedocs.io/en/master/api/tianshou.data.html#batch

from treevalue import FastTreeValue
from ..base import CMP_N, HAS_CUDA

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)
_BATCH_1 = Batch(**_TREE_DATA_1)

_TREE_DATA_2 = {'a': torch.randn(2, 3), 'x': {'c': torch.randn(3, 4)}}
_TREE_2 = FastTreeValue(_TREE_DATA_2)
_BATCH_2 = Batch(**_TREE_DATA_2)

if HAS_CUDA:
    _TREE_DATA_2_CUDA = nested_map(lambda x: x.cuda(), _TREE_DATA_2)

_TREE_DATA_3 = {'obs': torch.randn(4, 84, 84), 'action': torch.randint(0, 6, size=(1,)), 'reward': torch.rand(1)}
_TREE_3 = FastTreeValue(_TREE_DATA_3)
_BATCH_3 = Batch(**_TREE_DATA_3)


@pytest.mark.benchmark(group='tianshou-batch')
class TestCompareWithTianShouBatch:
    def __setup_tree(self):
        return FastTreeValue(_TREE_DATA_2)

    def __setup_tree_cuda(self):
        return FastTreeValue(_TREE_DATA_2_CUDA)

    def __setup_batch(self):
        return Batch(**_TREE_DATA_2)

    def __setup_batch_cuda(self):
        return Batch(**_TREE_DATA_2_CUDA)

    def test_tsb_init_ints(self, benchmark):
        benchmark(Batch, **_TREE_DATA_1)

    def test_tv_init_ints(self, benchmark):
        benchmark(FastTreeValue, _TREE_DATA_1)

    def test_tsb_init_tensors(self, benchmark):
        benchmark(Batch, **_TREE_DATA_2)

    def test_tv_init_tensors(self, benchmark):
        benchmark(FastTreeValue, _TREE_DATA_2)

    def test_tsb_getattr(self, benchmark):
        benchmark(getattr, _BATCH_2, 'a')

    def test_tv_getattr(self, benchmark):
        benchmark(getattr, _TREE_2, 'a')

    def test_tv_getattr_with_get(self, benchmark):
        benchmark(FastTreeValue.get, _TREE_2, 'a')

    def test_tsb_setattr(self, benchmark):
        benchmark(setattr, self.__setup_batch(), 'a', torch.randn(2, 3))

    def test_tv_setattr(self, benchmark):
        benchmark(setattr, self.__setup_tree(), 'a', torch.randn(2, 3))

    def test_tv_deepcopy(self, benchmark):
        benchmark(copy.deepcopy, _TREE_3)

    def test_tsb_deepcopy(self, benchmark):
        benchmark(copy.deepcopy, _BATCH_3)

    N = CMP_N
    _LEVELS = [2 ** i for i in range(N)]

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tsb_stack(self, benchmark, cnt):
        batches = [self.__setup_batch() for _ in range(cnt)]
        benchmark(Batch.stack, batches)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tsb_stack_cuda(self, benchmark, cnt):
        batches = [self.__setup_batch_cuda() for _ in range(cnt)]
        benchmark(Batch.stack, batches)

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tv_stack(self, benchmark, cnt):
        stack = FastTreeValue.func(subside=True)(torch.stack)
        trees = [self.__setup_tree() for _ in range(cnt)]
        benchmark(stack, trees)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tv_stack_cuda(self, benchmark, cnt):
        stack = FastTreeValue.func(subside=True)(torch.stack)
        trees = [self.__setup_tree_cuda() for _ in range(cnt)]
        benchmark(stack, trees)

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tsb_cat(self, benchmark, cnt):
        batches = [self.__setup_batch() for _ in range(cnt)]
        benchmark(Batch.cat, batches)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tsb_cat_cuda(self, benchmark, cnt):
        batches = [self.__setup_batch_cuda() for _ in range(cnt)]
        benchmark(Batch.cat, batches)

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tv_cat(self, benchmark, cnt):
        cat = FastTreeValue.func(subside=True)(torch.cat)
        trees = [self.__setup_tree() for _ in range(cnt)]
        benchmark(cat, trees)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tv_cat_cuda(self, benchmark, cnt):
        cat = FastTreeValue.func(subside=True)(torch.cat)
        trees = [self.__setup_tree_cuda() for _ in range(cnt)]
        benchmark(cat, trees)

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tsb_split(self, benchmark, cnt):
        def split(*args, **kwargs):
            return list(Batch.split(*args, **kwargs))

        batch = Batch({
            'obs': torch.randn(cnt, 4, 84, 84),
            'action': torch.randint(0, 6, size=(cnt, 1,)),
            'reward': torch.rand(cnt, 1),
        })
        benchmark(split, batch, 1, shuffle=False, merge_last=True)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tsb_split_cuda(self, benchmark, cnt):
        def split(*args, **kwargs):
            return list(Batch.split(*args, **kwargs))

        batch = Batch({
            'obs': torch.randn(cnt, 4, 84, 84).cuda(),
            'action': torch.randint(0, 6, size=(cnt, 1,)).cuda(),
            'reward': torch.rand(cnt, 1).cuda(),
        })
        benchmark(split, batch, 1, shuffle=False, merge_last=True)

    @pytest.mark.parametrize('cnt', _LEVELS)
    def test_tv_split(self, benchmark, cnt):
        split = FastTreeValue.func(rise=True)(torch.split)
        tree = FastTreeValue({
            'obs': torch.randn(cnt, 4, 84, 84),
            'action': torch.randint(0, 6, size=(cnt, 1,)),
            'reward': torch.rand(cnt, 1),
        })
        benchmark(split, tree, 1)

    @pytest.mark.parametrize('cnt', _LEVELS)
    @skipUnless(HAS_CUDA, 'CUDA required')
    def test_tv_split_cuda(self, benchmark, cnt):
        split = FastTreeValue.func(rise=True)(torch.split)
        tree = FastTreeValue({
            'obs': torch.randn(cnt, 4, 84, 84).cuda(),
            'action': torch.randint(0, 6, size=(cnt, 1,)).cuda(),
            'reward': torch.rand(cnt, 1).cuda(),
        })
        benchmark(split, tree, 1)
