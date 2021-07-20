import pytest

from treevalue.utils import SingletonMeta


@pytest.mark.unittest
class TestUtilsSingleton:
    def test_singleton(self):
        class T(metaclass=SingletonMeta):
            def get(self):
                return 1

        t = T()
        assert t is T()
        assert t.get() == 1

        class T2(T):
            def get(self):
                return 2

        tt = T2()
        assert tt is T2()
        assert tt is not t
        assert tt.get() == 2
