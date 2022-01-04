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

    def test_outer_inherit_without_missing(self):
        with pytest.warns(RuntimeWarning):
            @func_treelize('outer')
            def ssum(*args):
                return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        t3 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44, 'p': 76, 'e': 45}, 'f': 344})
        assert ssum(1, 2, 3) == 6
        assert ssum(t1, t2) == TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert ssum(t1.x, t2.x) == TreeValue({'c': 36, 'd': 48})

        with pytest.raises(KeyError):
            _ = ssum(t1, t3)

    def test_delayed_treelize(self):
        t1 = TreeValue({
            'a': 1, 'x': {'c': 3, 'd': 4},
        })
        t2 = TreeValue({
            'a': 11, 'b': 23, 'x': {'c': 35, },
        })

        cnt_1 = 0

        @func_treelize(delayed=True, mode='outer', missing=0)
        def total(a, b):
            nonlocal cnt_1
            cnt_1 += 1
            return a + b

        # positional
        t3 = total(t1, t2)
        assert cnt_1 == 0

        assert t3.a == 12
        assert cnt_1 == 1
        assert t3.x == TreeValue({'c': 38, 'd': 4})
        assert cnt_1 == 3
        assert t3 == TreeValue({
            'a': 12, 'b': 23, 'x': {'c': 38, 'd': 4}
        })
        assert cnt_1 == 4

        # keyword
        cnt_1 = 0
        t3 = total(a=t1, b=t2)
        assert cnt_1 == 0

        assert t3.a == 12
        assert cnt_1 == 1
        assert t3.x == TreeValue({'c': 38, 'd': 4})
        assert cnt_1 == 3
        assert t3 == TreeValue({
            'a': 12, 'b': 23, 'x': {'c': 38, 'd': 4}
        })
        assert cnt_1 == 4
