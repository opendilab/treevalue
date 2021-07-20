import pytest

from treevalue.tree import func_treelize, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncLeft:
    def test_left_raw(self):
        @func_treelize('left')
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})

        t3 = TreeValue({'a': 11, 'b': 22, 'c': 33, 'x': {'c': 33, 'd': 44, 'e': 550}})
        assert ssum(t1, t2, t3) == TreeValue({'a': 23, 'b': 46, 'x': {'c': 69, 'd': 92}})
        assert ssum(t2, t3) == TreeValue({'a': 22, 'b': 44, 'x': {'c': 66, 'd': 88}})
        with pytest.raises(KeyError):
            _ = ssum(t3, t1, t2)

    def test_left_missing(self):
        @func_treelize('left', missing=0)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        t3 = TreeValue({'a': 11, 'b': 22, 'c': 33, 'x': {'c': 33, 'd': 44, 'e': 550}})
        assert ssum(t1, t2, t3) == TreeValue({'a': 23, 'b': 46, 'x': {'c': 69, 'd': 92}})
        assert ssum(t2, t3) == TreeValue({'a': 22, 'b': 44, 'x': {'c': 66, 'd': 88}})
        assert ssum(t3, t1, t2) == TreeValue({'a': 23, 'b': 46, 'c': 33, 'x': {'c': 69, 'd': 92, 'e': 550}})

    def test_left_inherit(self):
        @func_treelize('left', missing=0, inherit=True)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        t3 = TreeValue({'a': 11, 'b': 22, 'c': 33, 'x': {'c': 33, 'd': 44, 'e': 550}})
        assert ssum(t3, t1, t2, -10) == TreeValue({'a': 13, 'b': 36, 'c': 23, 'x': {'c': 59, 'd': 82, 'e': 540}})
