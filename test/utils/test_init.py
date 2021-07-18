import pytest

from treevalue.utils import init_magic


@pytest.mark.unittest
class TestUtilsInit:
    def test_init_magic(self):
        def func_dc(func):
            def _new_func(x):
                return func(x + 1)

            return _new_func

        @init_magic(func_dc)
        class TT(object):
            def __init__(self, xx):
                self.__data = xx * xx

            @property
            def data(self):
                return self.__data

        class TT2(TT):
            def __init__(self, x):
                TT.__init__(self, x + 1)

        @init_magic(func_dc)
        class TT3(TT2):
            def __init__(self, x):
                TT2.__init__(self, x * 2)

        obj1 = TT3(233)
        assert obj1.data == 220900
        assert TT3.__name__ == 'TT3'
        assert TT.__name__ == 'TT'
