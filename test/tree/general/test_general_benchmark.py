import unittest
from functools import lru_cache
from typing import Optional

from hbutils.testing import vpip

try:
    import torch
except ImportError:
    torch = None

import pytest

from treevalue import TreeValue, func_treelize, FastTreeValue


@lru_cache()
def _get_tree() -> Optional[FastTreeValue]:
    if torch is not None:
        _TREE_DATA_1 = {'a': torch.randn(2, 3), 'x': {'c': torch.randn(3, 4)}}
        return FastTreeValue(_TREE_DATA_1)
    else:
        return None


@pytest.mark.benchmark(group='treevalue_dynamic')
@unittest.skipUnless(vpip('torch') >= '1.1.0', 'Torch>=1.1.0 only')
class TestTreeGeneralBenchmark:
    def test_dynamic_execute(self, benchmark):
        def sin(t):
            return t.sin()

        return benchmark(sin, _get_tree())

    def test_static_execute(self, benchmark):
        sinf = func_treelize(return_type=TreeValue)(torch.sin)

        def sin(t):
            return sinf(t)

        return benchmark(sin, _get_tree())
