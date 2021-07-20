import pytest

from treevalue.tree import func_treelize, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncStrict:
    def test_strict_raw(self):
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

    def test_strict_inherit(self):
        @func_treelize(inherit=True)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})
        assert ssum(t1, 1) == TreeValue({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})
        assert ssum(t1, TreeValue({'a': 2, 'b': 3, 'x': 80})) == TreeValue({'a': 3, 'b': 5, 'x': {'c': 83, 'd': 84}})

    def test_strict_missing(self):
        def ssum(*args):
            return sum(args)

        with pytest.warns(RuntimeWarning):
            ssum = func_treelize(missing=0)(ssum)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        t3 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'dd': 44}})

        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        with pytest.raises(KeyError):
            _ = ssum(t1, t3)
