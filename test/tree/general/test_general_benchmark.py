import pytest
import torch

from treevalue import TreeValue, func_treelize, FastTreeValue

_TREE_DATA_1 = {'a': torch.randn(2, 3), 'x': {'c': torch.randn(3, 4)}}
_TREE_1 = FastTreeValue(_TREE_DATA_1)


@pytest.mark.benchmark(group='treevalue_dynamic')
class TestTreeGeneralBenchmark:
    def test_dynamic_execute(self, benchmark):
        def sin(t):
            return t.sin()

        return benchmark(sin, _TREE_1)

    def test_static_execute(self, benchmark):
        sinf = func_treelize(return_type=TreeValue)(torch.sin)

        def sin(t):
            return sinf(t)

        return benchmark(sin, _TREE_1)
