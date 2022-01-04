import pytest

from treevalue.tree.common import DelayedProxy, delayed_partial


@pytest.mark.unittest
class TestTreeDelay:
    def test_delayed_partial_simple(self):
        cnt = 0

        def f():
            nonlocal cnt
            cnt += 1
            return 1

        pv = delayed_partial(f)
        assert cnt == 0
        assert isinstance(pv, DelayedProxy)

        assert pv.value() == 1
        assert cnt == 1

        assert pv.value() == 1
        assert cnt == 1

    def test_delayed_partial_func(self):
        cnt = 0

        def f(x, y):
            nonlocal cnt
            cnt += 1
            return x + y * 2 + 1

        pv = delayed_partial(f, 2, y=3)
        assert cnt == 0
        assert isinstance(pv, DelayedProxy)

        assert pv.value() == 9
        assert cnt == 1

        assert pv.value() == 9
        assert cnt == 1

    def test_delayed_partial_complex(self):
        cnt1, cnt2 = 0, 0

        def f1():
            nonlocal cnt1
            cnt1 += 1
            return 1

        def f2(x, y):
            nonlocal cnt2
            cnt2 += 1
            return (x + 1) ** 2 + y + 2

        pv = delayed_partial(f2, delayed_partial(f1), delayed_partial(f1))
        assert cnt1 == 0
        assert cnt2 == 0
        assert isinstance(pv, DelayedProxy)

        assert pv.value() == 7
        assert cnt1 == 2
        assert cnt2 == 1

        assert pv.value() == 7
        assert cnt1 == 2
        assert cnt2 == 1
