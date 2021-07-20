import pytest

from treevalue.utils import SingletonMeta, ValueBasedSingletonMeta, SingletonMark


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

    def test_value_based_singleton(self):
        class T(metaclass=ValueBasedSingletonMeta):
            def __init__(self, value):
                self.__value = value

            @property
            def value(self):
                return self.__value

        t = T(1)
        assert T(1) is t

        t2 = T(2)
        assert T(2) is not t
        assert T(2) is t2

    def test_singleton_mark(self):
        mark1 = SingletonMark("mark1")
        assert SingletonMark("mark1") is mark1
        assert SingletonMark("mark2") is not mark1
        assert mark1.mark == "mark1"

        h = {
            SingletonMark("mark1"): 1,
            SingletonMark("mark2"): 2,
        }
        assert h[SingletonMark("mark1")] == 1
        assert h[SingletonMark("mark2")] == 2

        assert mark1 == mark1
        assert mark1 != 2
        assert mark1 == SingletonMark("mark1")
        assert mark1 != SingletonMark("mark2")

        assert repr(mark1) == "<SingletonMark 'mark1'>"
