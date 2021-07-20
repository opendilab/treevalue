import pytest

from treevalue.tree import func_treelize, TreeMode, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncFunc:
    def test_tree_mode(self):
        assert TreeMode.loads(1) == TreeMode.STRICT
        assert TreeMode.loads(2) == TreeMode.LEFT
        assert TreeMode.loads(3) == TreeMode.INNER
        assert TreeMode.loads(4) == TreeMode.OUTER
        assert TreeMode.loads('strict') == TreeMode.STRICT
        assert TreeMode.loads('LEFT') == TreeMode.LEFT
        assert TreeMode.loads('Inner') == TreeMode.INNER
        assert TreeMode.loads('OuTeR') == TreeMode.OUTER
        assert TreeMode.loads(TreeMode.STRICT) == TreeMode.STRICT
        assert TreeMode.loads(TreeMode.LEFT) == TreeMode.LEFT
        assert TreeMode.loads(TreeMode.INNER) == TreeMode.INNER
        assert TreeMode.loads(TreeMode.OUTER) == TreeMode.OUTER

    def test_func_treelize_raw(self):
        @func_treelize()
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        t3 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'dd': 44}})

        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})
        with pytest.raises(KeyError):
            _ = ssum(t1, t3)
        with pytest.raises(TypeError):
            _ = ssum(t1, 1)

    def test_func_treelize_with_inherit(self):
        @func_treelize(allow_inherit=True)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})
        assert ssum(t1, 1) == TreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
        assert ssum(t1, TreeValue({'a': 2, 'b': 3, 'x': 80})) == TreeValue({'a': 3, 'b': 5, 'x': {'c': 83, 'd': 84}})
