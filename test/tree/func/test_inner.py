import pytest

from treevalue.tree import func_treelize, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncInner:
    def test_inner_raw(self):
        @func_treelize('inner')
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})
        with pytest.raises(TypeError):
            _ = ssum(t1, t2, 3)

        t3 = TreeValue({'a': 11, 'b': 22, 'c': 33, 'x': {'c': 33, 'd': 44, 'e': 550}})
        assert ssum(t1, t2, t3) == TreeValue({'a': 23, 'b': 46, 'x': {'c': 69, 'd': 92}})
        assert ssum(t2, t3) == TreeValue({'a': 22, 'b': 44, 'x': {'c': 66, 'd': 88}})
        assert ssum(t3, t1, t2) == TreeValue({'a': 23, 'b': 46, 'x': {'c': 69, 'd': 92}})

    def test_inner_inherit(self):
        @func_treelize('inner', allow_inherit=True)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1, t2, 3) == TreeValue({'a': 15, 'b': 27, 'x': {'c': 39, 'd': 51}})
