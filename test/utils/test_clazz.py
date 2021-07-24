import pytest
from easydict import EasyDict

from treevalue.tree import FastTreeValue, TreeValue
from treevalue.utils import init_magic, common_direct_base, common_bases


@pytest.mark.unittest
class TestUtilsClazz:
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

    def test_common_bases(self):
        assert common_bases(FastTreeValue, TreeValue) == {TreeValue}
        assert common_bases(FastTreeValue, TreeValue, str) == {object}
        assert common_bases(FastTreeValue, TreeValue, base=str) == set()
        assert common_bases() == set()

        class T1:
            pass

        class T2:
            pass

        class T3(T1, T2):
            pass

        class T4(T1, T2):
            pass

        class T5(T2, T1):
            pass

        assert common_bases(T1, T2, T3) == {object}
        assert common_bases(T3, T4) == {T1, T2}
        assert common_bases(T4, T5) == {T1, T2}

    def test_common_direct_base(self):
        assert common_direct_base(EasyDict, dict) == dict
        assert common_direct_base(EasyDict, str) == object

        with pytest.raises(TypeError):
            _ = common_direct_base()
        with pytest.raises(TypeError):
            _ = common_direct_base(EasyDict, str, base=dict)

        class T1:
            pass

        class T2:
            pass

        class T3(T1, T2):
            pass

        class T4(T1, T2):
            pass

        class T5(T2, T1):
            pass

        assert common_direct_base(T3, T4) == T1
        assert common_direct_base(T4, T5) == object
