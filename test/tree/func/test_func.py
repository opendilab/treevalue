from functools import reduce
from operator import __mul__

import pytest

from treevalue.tree import func_treelize, TreeValue, method_treelize, classmethod_treelize


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncFunc:
    def test_tree_value_type(self):
        class _MyTreeValue(TreeValue):
            pass

        @func_treelize(return_type=_MyTreeValue)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        tr1 = ssum(t1, t2)
        assert tr1 != TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert tr1 == _MyTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert isinstance(tr1, _MyTreeValue)
        assert isinstance(tr1.x, _MyTreeValue)

        @func_treelize(return_type=_MyTreeValue)
        def ssum2(*args):
            return sum(args), reduce(__mul__, args, 1)

        tr2 = ssum2(t1, t2)
        assert tr2 == _MyTreeValue({'a': (12, 11), 'b': (24, 44), 'x': {'c': (36, 99), 'd': (48, 176)}})

        @func_treelize(return_type=_MyTreeValue, rise=True)
        def ssum3(*args):
            return sum(args), reduce(__mul__, args, 1)

        tr3, tr4 = ssum3(t1, t2)
        assert tr3 == _MyTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert tr4 == _MyTreeValue({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 176}})

        @func_treelize(return_type=_MyTreeValue, subside=True, rise=dict(template=(None, None)))
        def ssum4(args):
            return sum(args), reduce(__mul__, args, 1)

        tr5, tr6 = ssum4([t1, t2])
        assert tr5 == _MyTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert tr6 == _MyTreeValue({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 176}})

        @func_treelize()
        def ssum5(a, b, c):
            return a + b * c

        t3 = TreeValue({'a': 31, 'b': 12, 'x': {'c': 43, 'd': 24}})
        assert ssum5(1, c=3, b=5) == 16
        assert ssum5(t2, c=t1, b=t3) == TreeValue({
            'a': 42,
            'b': 46,
            'x': {
                'c': 162,
                'd': 140,
            }
        })
        assert ssum5(t2, c=2, b=t3) == TreeValue({
            'a': 73,
            'b': 46,
            'x': {
                'c': 119,
                'd': 92,
            }
        })

        @func_treelize('outer', missing=lambda: 1)
        def ssum6(a, b, c):
            return a + b * c

        t4 = TreeValue({'a': 31, 'b': 12, 'x': {'c': 43}})
        with pytest.raises(KeyError):
            ssum5(t2, c=2, b=t4)
        assert ssum6(t2, c=2, b=t4) == TreeValue({
            'a': 73,
            'b': 46,
            'x': {
                'c': 119,
                'd': 46,
            }
        })

        @func_treelize('left')
        def ssum7(a, b, c):
            return a + b * c

        with pytest.raises(KeyError):
            ssum7(t2, c=2, b=t4)

        @func_treelize(inherit=False)
        def ssum8(a, b, c):
            return a + b * c

        with pytest.raises(TypeError):
            ssum8(t2, c=2, b=t1)

    def test_tree_value_type_none(self):
        @func_treelize(return_type=None)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        tr1 = ssum(t1, t2)
        assert tr1 is None

    def test_tree_value_type_invalid(self):
        class _MyTreeValue:
            pass

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            @func_treelize(return_type=_MyTreeValue)
            def ssum(*args):
                return sum(args)

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            @func_treelize(return_type=233)
            def ssum(*args):
                return sum(args)

    def test_method_treelize(self):
        class TreeNumber(TreeValue):
            @method_treelize()
            def _attr_extern(self, key):
                return getattr(self, key)

            @method_treelize('outer', missing=0)
            def __add__(self, other):
                return self + other

            @method_treelize('outer', missing=0)
            def __radd__(self, other):
                return other + self

            @method_treelize('outer', missing=0)
            def __sub__(self, other):
                return self - other

            @method_treelize('outer', missing=0)
            def __rsub__(self, other):
                return other - self

            @method_treelize()
            def __pos__(self):
                return +self

            @method_treelize()
            def __neg__(self):
                return -self

            @method_treelize()
            def __call__(self, *args, **kwargs):
                return self(*args, **kwargs)

            @method_treelize(return_type=TreeValue)
            def damn_it(self, x):
                return self + x

        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t1 + t2 + 1) == TreeNumber({'a': 13, 'b': 25, 'x': {'c': 37, 'd': 10}})
        assert (t1 - t2) == TreeNumber({'a': -10, 'b': -20, 'x': {'c': -30, 'd': -1}})
        assert (1 - t2) == TreeNumber({'a': -10, 'b': -21, 'x': {'c': -32, 'd': -4}})
        assert t1.damn_it(2) == TreeValue({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})

        class P:
            def __init__(self, value):
                self.__value = value

            @property
            def value(self):
                return self.__value

            def vv(self):
                return self.__value + 1

        ttt = TreeNumber({"a": P(1), "b": P(2), "x": {"c": P(3), "d": P(4)}})
        assert ttt.value == TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert ttt.vv() == TreeNumber({'a': 2, 'b': 3, 'x': {'c': 4, 'd': 5}})

        with pytest.warns(UserWarning):
            class MyTreeValue(TreeValue):
                @method_treelize(self_copy=True, rise=True)
                def __iadd__(self, other):
                    return self + other

    def test_classmethod_treelize(self):
        class TestUtils:
            @classmethod
            @classmethod_treelize('outer', missing=0, return_type=TreeValue)
            def add(cls, a, b):
                return cls, a + b

            @classmethod
            @classmethod_treelize(return_type=TreeValue)
            def add2(cls, a, b):
                return cls, a + b

        assert TestUtils.add(1, 2) == (TestUtils, 3)
        assert TestUtils.add(TreeValue({'a': 1, 'b': 2}), 2) == TreeValue({'a': (TestUtils, 3), 'b': (TestUtils, 4)})
        assert TestUtils.add2(TreeValue({'a': 1, 'b': 2}), TreeValue({'a': 12, 'b': 22})) == TreeValue(
            {'a': (TestUtils, 13), 'b': (TestUtils, 24)})

        class MyTreeValue(TreeValue):
            @classmethod
            @classmethod_treelize()
            def plus(cls, x, y):
                return x + y

        assert MyTreeValue.plus(TreeValue({'a': 1, 'b': 2}), 2) == MyTreeValue({'a': 3, 'b': 4})

    def test_missing(self):
        @func_treelize(mode='outer', missing=lambda: [])
        def append(arr: list, *args):
            for item in args:
                if item:
                    arr.append(item)
            return arr

        t0 = TreeValue({})
        t1 = TreeValue({'a': 2, 'b': 7, 'x': {'c': 4, 'd': 9}})
        t2 = TreeValue({'a': 4, 'b': 48, 'x': {'c': -11, 'd': 54}})
        t3 = TreeValue({'a': 9, 'b': -12, 'x': {'c': 3, 'd': 4}})

        assert append(t0, t1, t2, t3) == TreeValue({
            'a': [2, 4, 9],
            'b': [7, 48, -12],
            'x': {
                'c': [4, -11, 3],
                'd': [9, 54, 4],
            }
        })

        t0 = TreeValue({})
        t1 = TreeValue({'a': 2, 'x': {'c': 4, 'd': 9}})
        t2 = TreeValue({'a': 4, 'b': 48, 'x': {'d': 54}})
        t3 = TreeValue({'b': -12, 'x': 7, 'y': {'e': 3, 'f': 4}})

        assert append(t0, t1, t2, t3) == TreeValue({
            'a': [2, 4],
            'b': [48, -12],
            'x': {
                'c': [4, 7],
                'd': [9, 54, 7],
            },
            'y': {
                'e': [3],
                'f': [4],
            },
        })
