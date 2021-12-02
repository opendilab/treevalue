import pytest
import torch
from tianshou.data import Batch  # tianshou Batch https://tianshou.readthedocs.io/en/master/api/tianshou.data.html#batch

from treevalue import FastTreeValue

_TREE_DATA_1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)
_BATCH_1 = Batch(**_TREE_DATA_1)

_TREE_DATA_2 = {'a': torch.randn(2, 3), 'x': {'c': torch.randn(3, 4)}}
_TREE_2 = FastTreeValue(_TREE_DATA_2)
_BATCH_2 = Batch(**_TREE_DATA_2)

_TREE_DATA_3 = {'a': torch.randn(30, 40), 'x': {'c': torch.randn(30, 50)}}
_TREE_3 = FastTreeValue(_TREE_DATA_3)
_BATCH_3 = Batch(**_TREE_DATA_3)


@pytest.mark.benchmark(group='tianshou-batch')
class TestCompareWithTianShouBatch:
    def __setup_tree(self):
        return FastTreeValue(_TREE_DATA_2)

    def __setup_batch(self):
        return Batch(**_TREE_DATA_2)

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

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tsb_stack(self, benchmark, cnt):
        batches = [self.__setup_batch() for _ in range(cnt)]
        benchmark(Batch.stack, batches)

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tv_stack(self, benchmark, cnt):
        stack = FastTreeValue.func(subside=True)(torch.stack)
        trees = [self.__setup_tree() for _ in range(cnt)]
        benchmark(stack, trees)

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tsb_cat(self, benchmark, cnt):
        batches = [self.__setup_batch() for _ in range(cnt)]
        benchmark(Batch.cat, batches)

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tv_cat(self, benchmark, cnt):
        cat = FastTreeValue.func(subside=True)(torch.cat)
        trees = [self.__setup_tree() for _ in range(cnt)]
        benchmark(cat, trees)

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tsb_split(self, benchmark, cnt):
        def split(*args, **kwargs):
            return list(Batch.split(*args, **kwargs))

        benchmark(split, _BATCH_3, cnt, shuffle=False, merge_last=True)

    @pytest.mark.parametrize('cnt', [3, 10])
    def test_tv_split(self, benchmark, cnt):
        split = FastTreeValue.func(rise=True)(torch.split)
        benchmark(split, _TREE_3, cnt)
