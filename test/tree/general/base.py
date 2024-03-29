import collections.abc
import unittest
from functools import reduce
from operator import __mul__
from typing import Type

import numpy as np
import pytest
from hbutils.testing import cmdv

from treevalue import register_dict_type
from treevalue.tree import func_treelize, TreeValue, raw, mapping, delayed, FastTreeValue
from ..tree.base import get_treevalue_test
from ...testings import CustomMapping



def get_fasttreevalue_test(treevalue_class: Type[FastTreeValue]):
    class Container:
        def __init__(self, value):
            self.__value = value

        @property
        def value(self):
            return self.__value

        def add(self, x):
            return self.__value + x

        def __hash__(self) -> int:
            return hash(self.__value)

        def __eq__(self, other):
            if other is self:
                return True
            elif type(self) == type(other):
                return self.__value == other.__value
            else:
                return False

        def __repr__(self):
            return "<{cls} value: {value}>".format(cls=type(self).__name__, value=repr(self.__value))

    # noinspection DuplicatedCode,PyMethodMayBeStatic
    @pytest.mark.unittest
    class _TestClass(get_treevalue_test(treevalue_class)):
        def test_basic_methods(self):
            t3 = treevalue_class({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})
            assert t3.json() == {'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}}

            t5 = t3.x.clone()
            assert t5 == treevalue_class({'c': 38, 'd': 11})

        def test_numeric_add(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 + t1 + t2) == treevalue_class({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t3 = t1 + t2
            t1 += t2
            assert t1 == t3
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_sub(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 - t1 - t2) == treevalue_class({'a': -10, 'b': -22, 'x': {'c': -34, 'd': -7}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t3 = t1 - t2
            t1 -= t2
            assert t1 == t3
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_mul(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 * t1 * t2) == treevalue_class({'a': 22, 'b': 88, 'x': {'c': 198, 'd': 40}})

            i, j = 1, 1.0
            assert i.__mul__(j) == NotImplemented
            assert j.__mul__(i) == 1.0
            assert i * j == j.__mul__(i)

            t3 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5.2}})
            assert (t1 * t3) == treevalue_class({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 20.8}})
            assert (t3 * t1) == treevalue_class({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 20.8}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 * t2
            t1 *= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_matmul(self):
            t1 = treevalue_class({
                'a': np.array([[1, 2], [3, 4]]),
                'b': np.array([[2, 3], [4, 5]]),
                'x': {
                    'c': np.array([[3, 4], [5, 6]]),
                    'd': np.array([[4, 5], [6, 7]]),
                }
            })
            t2 = treevalue_class({
                'a': np.array([[4, 5], [6, 7]]),
                'b': np.array([[3, 4], [5, 6]]),
                'x': {
                    'c': np.array([[2, 3], [4, 5]]),
                    'd': np.array([[1, 2], [3, 4]]),
                }
            })

            tnp_array_equal = func_treelize(return_type=treevalue_class)(np.array_equal)
            assert tnp_array_equal((t1 @ t2), treevalue_class({
                'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
                'b': np.array([[2, 3], [4, 5]]) @ np.array([[3, 4], [5, 6]]),
                'x': {
                    'c': np.array([[3, 4], [5, 6]]) @ np.array([[2, 3], [4, 5]]),
                    'd': np.array([[4, 5], [6, 7]]) @ np.array([[1, 2], [3, 4]]),
                }
            })) == treevalue_class({
                'a': True,
                'b': True,
                'x': {
                    'c': True,
                    'd': True,
                }
            })
            assert tnp_array_equal(
                (t2.__rmatmul__(np.array([[1, 2], [3, 4]]))), treevalue_class({
                    'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
                    'b': np.array([[1, 2], [3, 4]]) @ np.array([[3, 4], [5, 6]]),
                    'x': {
                        'c': np.array([[1, 2], [3, 4]]) @ np.array([[2, 3], [4, 5]]),
                        'd': np.array([[1, 2], [3, 4]]) @ np.array([[1, 2], [3, 4]]),
                    }
                })
            ) == treevalue_class({
                'a': True,
                'b': True,
                'x': {
                    'c': True,
                    'd': True,
                }
            })

            class Ft:
                def __init__(self, x):
                    self.x = x
                    self.c = 0
                    self.rc = 0
                    self.ic = 0

                def __matmul__(self, other):
                    self.c += 1
                    return Ft(self.x @ other.x)

                def __rmatmul__(self, other):
                    self.rc += 1
                    return Ft(other.x @ self.x)

                def __imatmul__(self, other):
                    self.ic += 1
                    self.x = self.x @ other.x
                    return self

            tt1 = mapping(t1, lambda x, p: Ft(x))
            tt2 = mapping(t2, lambda x, p: Ft(x))

            original_id = id(tt1._detach())
            original_id_x = id(tt1.x._detach())
            tt4 = tt1 @ tt2
            tt1 @= tt2
            assert tnp_array_equal(tt1.x, tt4.x)
            assert tt1.a.c == 1
            assert tt1.a.rc == 0
            assert tt1.a.ic == 1

            assert id(tt1._detach()) == original_id
            assert id(tt1.x._detach()) == original_id_x

        def test_numeric_floordiv(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 / t1) == treevalue_class({'a': 11.0, 'b': 11.0, 'x': {'c': 11.0, 'd': 1.25}})
            assert (6 / t1) == treevalue_class({'a': 6.0, 'b': 3.0, 'x': {'c': 2.0, 'd': 1.5}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 / t2
            t1 /= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_truediv(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 // t1) == treevalue_class({'a': 11, 'b': 11, 'x': {'c': 11, 'd': 1}})
            assert (6 // t1) == treevalue_class({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 // t2
            t1 //= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_mod(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 % t1) == treevalue_class({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 1}})
            assert (6 % t1) == treevalue_class({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 2}})

            original_id = id(t2._detach())
            original_id_x = id(t2.x._detach())
            t4 = t2 % t1
            t2 %= t1
            assert t2 == t4
            assert id(t2._detach()) == original_id
            assert id(t2.x._detach()) == original_id_x

        def test_numeric_power(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert (t1 ** t1) == treevalue_class({'a': 1, 'b': 4, 'x': {'c': 27, 'd': 256}})
            assert (2 ** t1) == treevalue_class({'a': 2, 'b': 4, 'x': {'c': 8, 'd': 16}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 ** t1
            t1 **= t1
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_and(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 & t2) == treevalue_class({'a': 1, 'b': 2, 'x': {'c': 1, 'd': 4}})
            assert (7 & t2) == treevalue_class({'a': 3, 'b': 6, 'x': {'c': 1, 'd': 5}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 & t2
            t1 &= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_or(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 | t2) == treevalue_class({'a': 11, 'b': 22, 'x': {'c': 35, 'd': 5}})
            assert (7 | t2) == treevalue_class({'a': 15, 'b': 23, 'x': {'c': 39, 'd': 7}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 | t2
            t1 |= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_xor(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 ^ t2) == treevalue_class({'a': 10, 'b': 20, 'x': {'c': 34, 'd': 1}})
            assert (7 ^ t2) == treevalue_class({'a': 12, 'b': 17, 'x': {'c': 38, 'd': 2}})

            original_id = id(t1._detach())
            original_id_x = id(t1.x._detach())
            t4 = t1 ^ t2
            t1 ^= t2
            assert t1 == t4
            assert id(t1._detach()) == original_id
            assert id(t1.x._detach()) == original_id_x

        def test_numeric_lshift(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 << t1) == treevalue_class({'a': 22, 'b': 88, 'x': {'c': 264, 'd': 80}})
            assert (3 << t1) == treevalue_class({'a': 6, 'b': 12, 'x': {'c': 24, 'd': 48}})

            original_id = id(t2._detach())
            original_id_x = id(t2.x._detach())
            t4 = t2 << t1
            t2 <<= t1
            assert t2 == t4
            assert id(t2._detach()) == original_id
            assert id(t2.x._detach()) == original_id_x

        def test_numeric_rshift(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 >> t1) == treevalue_class({'a': 5, 'b': 5, 'x': {'c': 4, 'd': 0}})
            assert (32 >> t1) == treevalue_class({'a': 16, 'b': 8, 'x': {'c': 4, 'd': 2}})

            original_id = id(t2._detach())
            original_id_x = id(t2.x._detach())
            t4 = t2 >> t1
            t2 >>= t1
            assert t2 == t4
            assert id(t2._detach()) == original_id
            assert id(t2.x._detach()) == original_id_x

        def test_numeric_pos(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert +t1 == treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        def test_numeric_neg(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert -t1 == treevalue_class({'a': -1, 'b': -2, 'x': {'c': -3, 'd': -4}})

        def test_numeric_invert(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert ~t1 == treevalue_class({'a': -2, 'b': -3, 'x': {'c': -4, 'd': -5}})

        def test_getitem(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                  'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            assert t2[t1 - 1] == treevalue_class({'a': 2, 'b': 13, 'x': {'c': 31, 'd': 53}})
            assert t2['a'] == [2, 3, 5, 7]
            assert t2['x'] == treevalue_class({'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]})
            assert t2['x']['c'] == [23, 29, 31, 37]

            m1 = np.random.random((3, 4))
            m2 = np.random.random((3, 5))
            a = treevalue_class({'a': m1, 'b': m2})
            assert np.allclose(a['a'], m1)
            assert np.allclose(a['b'], m2)

            a0 = a[0]
            assert np.allclose(a0['a'], m1[0])
            assert np.allclose(a0['b'], m2[0])

            a_35 = a[:, 3:5]
            assert np.allclose(a_35['a'], m1[:, 3:5])
            assert np.allclose(a_35['b'], m2[:, 3:5])

            b = treevalue_class({'': m1, '1': m2})
            assert np.allclose(b[''], m1)
            assert np.allclose(b['1'], m2)

            t3 = treevalue_class({
                'a': raw({'a': 1, 'y': 2}),
                'c': {'x': raw({'a': 3, 'y': 4})},
            })
            assert t3['a'] == {'a': 1, 'y': 2}
            assert t3['c'] == treevalue_class({'x': raw({'a': 3, 'y': 4})})
            assert t3['c']['x'] == {'a': 3, 'y': 4}
            with pytest.raises(KeyError):
                _ = t3['y']

            assert t3[['a']] == treevalue_class({'a': 1, 'c': {'x': 3}})
            assert t3[['y']] == treevalue_class({'a': 2, 'c': {'x': 4}})

        def test_setitem(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                  'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            t2[t1 - 1] = t1
            assert t2 == treevalue_class({'a': [1, 3, 5, 7], 'b': [11, 2, 17, 19],
                                          'x': {'c': [23, 29, 3, 37], 'd': [41, 43, 47, 4]}})

            t3 = treevalue_class({
                'a': raw({'a': 1, 'y': 2}),
                'c': {'x': raw({'a': 3, 'y': 4})},
            })
            t3['a'] = {'a': 11, 'y': 22}
            assert t3 == treevalue_class({
                'a': raw({'a': 11, 'y': 22}),
                'c': {'x': raw({'a': 3, 'y': 4})},
            })
            t3[['a']] = 33
            assert t3 == treevalue_class({
                'a': raw({'a': 33, 'y': 22}),
                'c': {'x': raw({'a': 33, 'y': 4})},
            })
            t3[['y']] = 55
            assert t3 == treevalue_class({
                'a': raw({'a': 33, 'y': 55}),
                'c': {'x': raw({'a': 33, 'y': 55})},
            })

        def test_delitem(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                  'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            del t2[t1 - 1]
            assert t2 == treevalue_class({'a': [3, 5, 7], 'b': [11, 17, 19],
                                          'x': {'c': [23, 29, 37], 'd': [41, 43, 47]}})

            t3 = treevalue_class({
                'a': raw({'a': 1, 'y': 2}),
                'c': {'x': raw({'a': 3, 'y': 4})},
                'g': 2,
            })
            del t3['g']
            assert t3 == treevalue_class({
                'a': raw({'a': 1, 'y': 2}),
                'c': {'x': raw({'a': 3, 'y': 4})},
            })

            with pytest.raises(KeyError):
                del t3[['g']]

            del t3[['a']]
            assert t3 == treevalue_class({
                'a': raw({'y': 2}),
                'c': {'x': raw({'y': 4})},
            })

            del t3['a']
            assert t3 == treevalue_class({
                'c': {'x': raw({'y': 4})},
            })

        def test_attr(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = func_treelize(return_type=treevalue_class)(Container)(t1)
            assert t2 == treevalue_class(
                {'a': Container(1), 'b': Container(2), 'x': {'c': Container(3), 'd': Container(4)}})
            assert t2.value == t1

            assert t1.a == 1
            assert t1.x == treevalue_class({'c': 3, 'd': 4})

            m1 = np.random.random((3, 4))
            m2 = np.random.random((3, 5))
            a = treevalue_class({'a': m1, 'b': m2})
            assert np.allclose(a.a, m1)
            assert np.allclose(a.b, m2)
            assert a.shape == treevalue_class({
                'a': (3, 4), 'b': (3, 5),
            })

        def test_call(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = func_treelize(return_type=treevalue_class)(Container)(t1)
            assert t2.add(10) == treevalue_class({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
            assert t2.add(x=10) == treevalue_class({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
            assert t2.add(t1) == treevalue_class({'a': 2, 'b': 4, 'x': {'c': 6, 'd': 8}})

        def test_map(self):
            cnt = 0

            def f(x):
                nonlocal cnt
                cnt += 1
                return x + 2

            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert cnt == 0
            t2 = t1.map(f)
            assert cnt == 4
            assert t2 == treevalue_class({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})

            cnt = 0
            t3 = treevalue_class({
                'a': delayed(lambda: t1.a),
                'b': delayed(lambda: t1.b),
                'x': delayed(lambda: t1.x),
            })
            assert cnt == 0

            t4 = t3.map(f, delayed=True)
            assert cnt == 0

            assert t4.a == 3
            assert cnt == 1

            assert t4 == treevalue_class({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})
            assert cnt == 4

            assert t4.a == 3
            assert cnt == 4

        def test_type(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.type(TreeValue) == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.type(TreeValue) != treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        def test_filter(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.filter(lambda x: x % 2 == 1) == treevalue_class({'a': 1, 'x': {'c': 3}})
            assert t1.filter(lambda x: x < 3) == treevalue_class({'a': 1, 'b': 2, })
            assert t1.filter(lambda x: x < 3, False) == treevalue_class({'a': 1, 'b': 2, 'x': {}})

        def test_mask(self):
            t1 = treevalue_class({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t3 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 7, 'd': 4}})

            mask1 = t2.map(lambda x: (lambda v: v % x == 0))(t1)
            assert t1.mask(mask1) == treevalue_class({'a': 13, 'x': {'c': 39}})

            mask2 = t3.map(lambda x: (lambda v: v % x == 0))(t1)
            assert t1.mask(mask2) == treevalue_class({'a': 13})
            assert t1.mask(mask2, False) == treevalue_class({'a': 13, 'x': {}})

        def test_reduce(self):
            t1 = treevalue_class({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

            assert t1.reduce(lambda **kwargs: sum(kwargs.values())) == 124
            assert t2.reduce(lambda **kwargs: reduce(__mul__, kwargs.values())) == 24

        def test_union(self):
            t1 = treevalue_class({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t3 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 7, 'd': 4}})

            assert treevalue_class.union(t1, t2, t3) == treevalue_class({
                'a': (13, 1, 1),
                'b': (27, 2, 2),
                'x': {
                    'c': (39, 3, 7),
                    'd': (45, 4, 4),
                }
            })

            assert treevalue_class.union(t1, t2, t3, return_type=TreeValue) == TreeValue({
                'a': (13, 1, 1),
                'b': (27, 2, 2),
                'x': {
                    'c': (39, 3, 7),
                    'd': (45, 4, 4),
                }
            })

        def test_subside(self):
            data = {
                'a': TreeValue({'a': 1, 'b': 2}),
                'x': {
                    'c': TreeValue({'a': 3, 'b': 4}),
                    'd': [
                        TreeValue({'a': 5, 'b': 6}),
                        TreeValue({'a': 7, 'b': 8}),
                    ]
                },
                'k': '233'
            }

            assert treevalue_class.subside(data) == treevalue_class({
                'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
                'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
            })
            assert treevalue_class.subside(data, return_type=TreeValue) == TreeValue({
                'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
                'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
            })

        def test_rise(self):
            data = {
                'a': TreeValue({'a': 1, 'b': 2}),
                'x': {
                    'c': TreeValue({'a': 3, 'b': 4}),
                    'd': [
                        TreeValue({'a': 5, 'b': 6}),
                        TreeValue({'a': 7, 'b': 8}),
                    ]
                },
                'k': '233'
            }

            t1 = treevalue_class.subside(data)
            assert t1.rise() == {
                'a': treevalue_class({'a': 1, 'b': 2}),
                'x': {
                    'c': treevalue_class({'a': 3, 'b': 4}),
                    'd': [
                        treevalue_class({'a': 5, 'b': 6}),
                        treevalue_class({'a': 7, 'b': 8}),
                    ]
                },
                'k': treevalue_class({'a': '233', 'b': '233'}),
            }

        def test_deep_clone(self):
            t = treevalue_class({
                'a': raw({'a': 1, 'b': 2}),
                'b': raw({'a': 3, 'b': 4}),
                'x': {
                    'c': raw({'a': 5, 'b': 6}),
                    'd': raw({'a': 7, 'b': 8}),
                }
            })

            t1 = t.clone()
            assert t1 == t
            assert t1.a is t.a
            assert t1.b is t.b
            assert t1.x.c is t.x.c
            assert t1.x.d is t.x.d

            t2 = t.clone(copy_value=True)
            assert t2 == t
            assert t2.a is not t.a
            assert t2.b is not t.b
            assert t2.x.c is not t.x.c
            assert t2.x.d is not t.x.d

        @unittest.skipUnless(cmdv('dot'), 'Dot installed only')
        def test_graph(self):
            t = treevalue_class({
                'a': [4, 3, 2, 1],
                'b': np.array([[5, 6], [7, 8]]),
                'x': {
                    'c': np.array([[5, 7], [8, 6]]),
                    'd': {'a', 'b', 'c'},
                    'e': np.array([[1, 2], [3, 4]])
                },
            })
            graph = t.graph('t')
            assert len(graph.source) <= 2290

        @unittest.skipUnless(cmdv('dot'), 'Dot installed only')
        def test_graphics(self):
            t = treevalue_class({
                'a': [4, 3, 2, 1],
                'b': np.array([[5, 6], [7, 8]]),
                'x': {
                    'c': np.array([[5, 7], [8, 6]]),
                    'd': {'a', 'b', 'c'},
                    'e': np.array([[1, 2], [3, 4]])
                },
            })
            t1 = treevalue_class({
                'aa': t.a,
                'bb': np.array([[5, 6], [7, 8]]),
                'xx': {
                    'cc': t.x.c,
                    'dd': t.x.d,
                    'ee': np.array([[1, 2], [3, 4]])
                },
            })

            graph_1 = treevalue_class.graphics(
                (t, 't'), (t1, 't1'),
                (treevalue_class({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=(np.ndarray, list),
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert len(graph_1.source) <= 5000  # a value for svg in windows

            graph_2 = treevalue_class.graphics(
                (t, 't'), (t1, 't1'),
                (treevalue_class({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=False,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert len(graph_2.source) <= 5600

            graph_3 = treevalue_class.graphics(
                (t, 't'), (t1, 't1'),
                (treevalue_class({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=lambda x: id(x),
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert len(graph_3.source) <= 4760

            graph_4 = treevalue_class.graphics(
                (t, 't'), (t1, 't1'),
                (treevalue_class({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=lambda x: type(x).__name__,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert len(graph_4.source) <= 4000

            graph_6 = treevalue_class.graphics(
                (t, 't'), (t1, 't1'),
                (treevalue_class({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=True,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert len(graph_6.source) <= 4760

        def test_func(self):
            t1 = treevalue_class({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = treevalue_class({'a': 11, 'b': 20, 'x': {'c': 33, 'd': 48}})

            @treevalue_class.func()
            def ssum(x, y):
                return x + y

            assert ssum(t1, t2) == treevalue_class({'a': 12, 'b': 22, 'x': {'c': 36, 'd': 52}})

            cnt_1 = 0

            @treevalue_class.func(delayed=True)
            def ssumx(x, y):
                nonlocal cnt_1
                cnt_1 += 1
                return x + y

            cnt_1 = 0
            t3 = ssumx(t1, t2)
            assert cnt_1 == 0

            assert t3.a == 12
            assert cnt_1 == 1
            assert t3.x == treevalue_class({'c': 36, 'd': 52})
            assert cnt_1 == 3
            assert t3 == treevalue_class({'a': 12, 'b': 22, 'x': {'c': 36, 'd': 52}})
            assert cnt_1 == 4

        def test_walk(self):
            tv1 = treevalue_class({'a': 1, 'b': 'dks', 'c': {'x': 2, 'y': 3}})
            assert dict(tv1.walk()) == {
                (): treevalue_class({'a': 1, 'b': 'dks', 'c': {'x': 2, 'y': 3}}),
                ('a',): 1,
                ('b',): 'dks',
                ('c',): treevalue_class({'x': 2, 'y': 3}),
                ('c', 'x'): 2,
                ('c', 'y'): 3,
            }

        def test_tree_value_operate_with_item(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            tv2 = treevalue_class(tv1)
            tv3 = treevalue_class({'a': tv1, 'b': tv2, 'c': tv1})
            tv4 = treevalue_class({'a': raw({'a': 1, 'y': 2}), 'c': {'x': raw({'a': 3, 'y': 4}), }})

            tv1['a'] = 3
            assert tv1.a == 3
            assert tv2.a == 3
            assert tv3.a.a == 3
            assert tv3.b.a == 3
            assert tv3.c.a == 3

            assert tv4['a'] == {'a': 1, 'y': 2}
            assert tv4['c'] == treevalue_class({'x': raw({'a': 3, 'y': 4})})
            with pytest.raises(KeyError):
                _ = tv4['y']
            with pytest.raises(KeyError):
                _ = tv4[['c']]

            tv1['f'] = 333
            assert tv1.f == 333
            assert tv1['f'] == 333
            assert 'f' in tv1

            with pytest.raises(TypeError):
                tv1[0] = 3
            with pytest.raises(TypeError):
                tv1[['c']] = 3

            del tv1['b']
            assert 'b' not in tv1
            assert 'b' not in tv2
            assert 'b' not in tv3.a
            assert 'b' not in tv3.b
            assert 'b' not in tv3.c

            with pytest.raises(KeyError):
                del tv1['g']
            with pytest.raises(TypeError):
                del tv1[['c']]
            with pytest.raises(TypeError):
                del tv1[0]

        def test_tree_value_init_with_item(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert tv1['a'] == 1
            assert tv1['b'] == 2

            tv2 = treevalue_class(tv1)
            assert tv2['a'] == 1
            assert tv2['b'] == 2

            tv3 = treevalue_class({'a': tv1, 'b': tv2, 'c': tv1})
            assert tv3['a']['a'] == 1
            assert tv3['b']['a'] == 1
            assert tv3['c']['a'] == 1

            with pytest.raises(KeyError):
                _ = tv3['g']
            with pytest.raises(TypeError):
                _ = tv3[0]

        def test_unpack(self):
            t1 = treevalue_class({
                'a': 21, 'b': {'x': 'f-49', 'y': 7.7},
            })
            a, b = t1.unpack('a', 'b')
            assert a == 21
            assert isinstance(b, treevalue_class)
            assert b.x == 'f-49'
            assert b.y == pytest.approx(7.7)

            x, y = b.unpack('x', 'y')
            assert x == 'f-49'
            assert y == pytest.approx(7.7)

            with pytest.raises(KeyError):
                _ = b.unpack('x', 'y', 'z')

            x, y, z = b.unpack('x', 'y', 'z', default=None)
            assert x == 'f-49'
            assert y == pytest.approx(7.7)
            assert z is None

        def test_init_with_custom_mapping_type(self):
            origin_t = CustomMapping(a=1, b=2, c={'x': 15, 'y': CustomMapping(z=100)})
            t = treevalue_class(origin_t)
            assert t == treevalue_class({'a': 1, 'b': 2, 'c': {'x': 15, 'y': {'z': 100}}})

        def test_init_with_custom_type(self):
            class _CustomMapping:
                def __init__(self, **kwargs):
                    self._kwargs = kwargs

                def __getitem__(self, __key):
                    return self._kwargs[__key]

                def __len__(self):
                    return len(self._kwargs)

                def __iter__(self):
                    yield from self._kwargs

                def iter_items(self):
                    yield from self._kwargs.items()

            register_dict_type(_CustomMapping, _CustomMapping.iter_items)

            origin_t = _CustomMapping(a=1, b=2, c={'x': 15, 'y': _CustomMapping(z=100)})
            t = treevalue_class(origin_t)
            assert t == treevalue_class({'a': 1, 'b': 2, 'c': {'x': 15, 'y': {'z': 100}}})

    return _TestClass
