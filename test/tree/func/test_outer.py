import pytest

from treevalue.tree import func_treelize, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncOuter:
    def test_outer_inherit(self):
        @func_treelize('outer', missing=lambda: 0)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44, 'p': 76, 'e': 45}, 'f': 344})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'f': 344, 'x': {'c': 36, 'd': 48, 'p': 76, 'e': 45}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48, 'p': 76, 'e': 45})

        t3 = TreeValue({'a': 11, 'b': 22, 'c': 33, 'x': {'c': 33, 'd': 44, 'e': 550, 'v': -100}})
        assert ssum(t1, t2, t3) == TreeValue({
            'a': 23, 'b': 46, 'c': 33, 'f': 344,
            'x': {'c': 69, 'd': 92, 'p': 76, 'e': 595, 'v': -100}
        })
