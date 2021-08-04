from functools import reduce
from operator import __mul__
from typing import Type

import numpy as np
import pytest

from treevalue.tree import func_treelize, TreeValue, raw
from treevalue.tree.tree.tree import get_data_property


def get_tree_test(tree_value_clazz: Type[TreeValue]):
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
    class _TestClass:
        def test_basic_methods(self):
            t3 = tree_value_clazz({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})
            assert t3.json() == {'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}}

            t4 = t3.view(['x'])
            t5 = t3.x.clone()
            assert t4 == tree_value_clazz({'c': 38, 'd': 11})
            assert t5 == tree_value_clazz({'c': 38, 'd': 11})
            t3.x.c = 100
            assert t4 == tree_value_clazz({'c': 100, 'd': 11})
            assert t5 == tree_value_clazz({'c': 38, 'd': 11})

        def test_numeric_add(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 + t1 + t2) == tree_value_clazz({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t3 = t1 + t2
            t1 += t2
            assert t1 == t3
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_sub(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 - t1 - t2) == tree_value_clazz({'a': -10, 'b': -22, 'x': {'c': -34, 'd': -7}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t3 = t1 - t2
            t1 -= t2
            assert t1 == t3
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_mul(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (2 * t1 * t2) == tree_value_clazz({'a': 22, 'b': 88, 'x': {'c': 198, 'd': 40}})

            i, j = 1, 1.0
            assert i.__mul__(j) == NotImplemented
            assert j.__mul__(i) == 1.0
            assert i * j == j.__mul__(i)

            t3 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5.2}})
            assert (t1 * t3) == tree_value_clazz({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 20.8}})
            assert (t3 * t1) == tree_value_clazz({'a': 11, 'b': 44, 'x': {'c': 99, 'd': 20.8}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 * t2
            t1 *= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_matmul(self):
            t1 = tree_value_clazz({
                'a': np.array([[1, 2], [3, 4]]),
                'b': np.array([[2, 3], [4, 5]]),
                'x': {
                    'c': np.array([[3, 4], [5, 6]]),
                    'd': np.array([[4, 5], [6, 7]]),
                }
            })
            t2 = tree_value_clazz({
                'a': np.array([[4, 5], [6, 7]]),
                'b': np.array([[3, 4], [5, 6]]),
                'x': {
                    'c': np.array([[2, 3], [4, 5]]),
                    'd': np.array([[1, 2], [3, 4]]),
                }
            })

            npeq = func_treelize(return_type=tree_value_clazz)(np.array_equal)
            assert npeq((t1 @ t2), tree_value_clazz({
                'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
                'b': np.array([[2, 3], [4, 5]]) @ np.array([[3, 4], [5, 6]]),
                'x': {
                    'c': np.array([[3, 4], [5, 6]]) @ np.array([[2, 3], [4, 5]]),
                    'd': np.array([[4, 5], [6, 7]]) @ np.array([[1, 2], [3, 4]]),
                }
            })) == tree_value_clazz({
                'a': True,
                'b': True,
                'x': {
                    'c': True,
                    'd': True,
                }
            })
            assert npeq(
                (t2.__rmatmul__(np.array([[1, 2], [3, 4]]))), tree_value_clazz({
                    'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
                    'b': np.array([[1, 2], [3, 4]]) @ np.array([[3, 4], [5, 6]]),
                    'x': {
                        'c': np.array([[1, 2], [3, 4]]) @ np.array([[2, 3], [4, 5]]),
                        'd': np.array([[1, 2], [3, 4]]) @ np.array([[1, 2], [3, 4]]),
                    }
                })
            ) == tree_value_clazz({
                'a': True,
                'b': True,
                'x': {
                    'c': True,
                    'd': True,
                }
            })

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 @ t2
            t1 @= t2
            assert npeq(t1, t4)
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_floordiv(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 / t1) == tree_value_clazz({'a': 11.0, 'b': 11.0, 'x': {'c': 11.0, 'd': 1.25}})
            assert (6 / t1) == tree_value_clazz({'a': 6.0, 'b': 3.0, 'x': {'c': 2.0, 'd': 1.5}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 / t2
            t1 /= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_truediv(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 // t1) == tree_value_clazz({'a': 11, 'b': 11, 'x': {'c': 11, 'd': 1}})
            assert (6 // t1) == tree_value_clazz({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 // t2
            t1 //= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_mod(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 % t1) == tree_value_clazz({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 1}})
            assert (6 % t1) == tree_value_clazz({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 2}})

            original_id = id(get_data_property(t2).actual())
            original_id_x = id(get_data_property(t2.x).actual())
            t4 = t2 % t1
            t2 %= t1
            assert t2 == t4
            assert id(get_data_property(t2).actual()) == original_id
            assert id(get_data_property(t2.x).actual()) == original_id_x

        def test_numeric_power(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert (t1 ** t1) == tree_value_clazz({'a': 1, 'b': 4, 'x': {'c': 27, 'd': 256}})
            assert (2 ** t1) == tree_value_clazz({'a': 2, 'b': 4, 'x': {'c': 8, 'd': 16}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 ** t1
            t1 **= t1
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_and(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 & t2) == tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 1, 'd': 4}})
            assert (7 & t2) == tree_value_clazz({'a': 3, 'b': 6, 'x': {'c': 1, 'd': 5}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 & t2
            t1 &= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_or(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 | t2) == tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 35, 'd': 5}})
            assert (7 | t2) == tree_value_clazz({'a': 15, 'b': 23, 'x': {'c': 39, 'd': 7}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 | t2
            t1 |= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_xor(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t1 ^ t2) == tree_value_clazz({'a': 10, 'b': 20, 'x': {'c': 34, 'd': 1}})
            assert (7 ^ t2) == tree_value_clazz({'a': 12, 'b': 17, 'x': {'c': 38, 'd': 2}})

            original_id = id(get_data_property(t1).actual())
            original_id_x = id(get_data_property(t1.x).actual())
            t4 = t1 ^ t2
            t1 ^= t2
            assert t1 == t4
            assert id(get_data_property(t1).actual()) == original_id
            assert id(get_data_property(t1.x).actual()) == original_id_x

        def test_numeric_lshift(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 << t1) == tree_value_clazz({'a': 22, 'b': 88, 'x': {'c': 264, 'd': 80}})
            assert (3 << t1) == tree_value_clazz({'a': 6, 'b': 12, 'x': {'c': 24, 'd': 48}})

            original_id = id(get_data_property(t2).actual())
            original_id_x = id(get_data_property(t2.x).actual())
            t4 = t2 << t1
            t2 <<= t1
            assert t2 == t4
            assert id(get_data_property(t2).actual()) == original_id
            assert id(get_data_property(t2.x).actual()) == original_id_x

        def test_numeric_rshift(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
            assert (t2 >> t1) == tree_value_clazz({'a': 5, 'b': 5, 'x': {'c': 4, 'd': 0}})
            assert (32 >> t1) == tree_value_clazz({'a': 16, 'b': 8, 'x': {'c': 4, 'd': 2}})

            original_id = id(get_data_property(t2).actual())
            original_id_x = id(get_data_property(t2.x).actual())
            t4 = t2 >> t1
            t2 >>= t1
            assert t2 == t4
            assert id(get_data_property(t2).actual()) == original_id
            assert id(get_data_property(t2.x).actual()) == original_id_x

        def test_numeric_pos(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert +t1 == tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        def test_numeric_neg(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert -t1 == tree_value_clazz({'a': -1, 'b': -2, 'x': {'c': -3, 'd': -4}})

        def test_numeric_invert(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert ~t1 == tree_value_clazz({'a': -2, 'b': -3, 'x': {'c': -4, 'd': -5}})

        def test_getitem(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                   'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            assert t2[t1 - 1] == tree_value_clazz({'a': 2, 'b': 13, 'x': {'c': 31, 'd': 53}})

        def test_setitem(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                   'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            t2[t1 - 1] = t1
            assert t2 == tree_value_clazz({'a': [1, 3, 5, 7], 'b': [11, 2, 17, 19],
                                           'x': {'c': [23, 29, 3, 37], 'd': [41, 43, 47, 4]}})

        def test_delitem(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = tree_value_clazz({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                                   'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

            del t2[t1 - 1]
            assert t2 == tree_value_clazz({'a': [3, 5, 7], 'b': [11, 17, 19],
                                           'x': {'c': [23, 29, 37], 'd': [41, 43, 47]}})

        def test_attr(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = func_treelize(return_type=tree_value_clazz)(Container)(t1)
            assert t2 == tree_value_clazz(
                {'a': Container(1), 'b': Container(2), 'x': {'c': Container(3), 'd': Container(4)}})
            assert t2.value == t1

        def test_call(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t2 = func_treelize(return_type=tree_value_clazz)(Container)(t1)
            assert t2.add(10) == tree_value_clazz({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
            assert t2.add(x=10) == tree_value_clazz({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
            assert t2.add(t1) == tree_value_clazz({'a': 2, 'b': 4, 'x': {'c': 6, 'd': 8}})

        def test_map(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.map(lambda x: x + 2) == tree_value_clazz({'a': 3, 'b': 4, 'x': {'c': 5, 'd': 6}})

        def test_type(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.type(TreeValue) == TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.type(TreeValue) != tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        def test_filter(self):
            t1 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            assert t1.filter(lambda x: x % 2 == 1) == tree_value_clazz({'a': 1, 'x': {'c': 3}})
            assert t1.filter(lambda x: x < 3) == tree_value_clazz({'a': 1, 'b': 2, })
            assert t1.filter(lambda x: x < 3, False) == tree_value_clazz({'a': 1, 'b': 2, 'x': {}})

        def test_mask(self):
            t1 = tree_value_clazz({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t3 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 7, 'd': 4}})

            mask1 = t2.map(lambda x: (lambda v: v % x == 0))(t1)
            assert t1.mask(mask1) == tree_value_clazz({'a': 13, 'x': {'c': 39}})

            mask2 = t3.map(lambda x: (lambda v: v % x == 0))(t1)
            assert t1.mask(mask2) == tree_value_clazz({'a': 13})
            assert t1.mask(mask2, False) == tree_value_clazz({'a': 13, 'x': {}})

        def test_reduce(self):
            t1 = tree_value_clazz({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

            assert t1.reduce(lambda **kwargs: sum(kwargs.values())) == 124
            assert t2.reduce(lambda **kwargs: reduce(__mul__, kwargs.values())) == 24

        def test_union(self):
            t1 = tree_value_clazz({'a': 13, 'b': 27, 'x': {'c': 39, 'd': 45}})
            t2 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
            t3 = tree_value_clazz({'a': 1, 'b': 2, 'x': {'c': 7, 'd': 4}})

            assert tree_value_clazz.union(t1, t2, t3) == tree_value_clazz({
                'a': (13, 1, 1),
                'b': (27, 2, 2),
                'x': {
                    'c': (39, 3, 7),
                    'd': (45, 4, 4),
                }
            })

            assert tree_value_clazz.union(t1, t2, t3, return_type=TreeValue) == TreeValue({
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

            assert tree_value_clazz.subside(data) == tree_value_clazz({
                'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
                'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
            })
            assert tree_value_clazz.subside(data, return_type=TreeValue) == TreeValue({
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

            t1 = tree_value_clazz.subside(data)
            assert t1.rise() == {
                'a': tree_value_clazz({'a': 1, 'b': 2}),
                'x': {
                    'c': tree_value_clazz({'a': 3, 'b': 4}),
                    'd': [
                        tree_value_clazz({'a': 5, 'b': 6}),
                        tree_value_clazz({'a': 7, 'b': 8}),
                    ]
                },
                'k': tree_value_clazz({'a': '233', 'b': '233'}),
            }

        def test_deep_clone(self):
            t = tree_value_clazz({
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

        def test_graph(self):
            t = tree_value_clazz({
                'a': [4, 3, 2, 1],
                'b': np.array([[5, 6], [7, 8]]),
                'x': {
                    'c': np.array([[5, 7], [8, 6]]),
                    'd': {'a', 'b', 'c'},
                    'e': np.array([[1, 2], [3, 4]])
                },
            })
            graph = t.graph('t')
            assert 2210 <= len(graph.source) <= 2290

        def test_graphics(self):
            t = tree_value_clazz({
                'a': [4, 3, 2, 1],
                'b': np.array([[5, 6], [7, 8]]),
                'x': {
                    'c': np.array([[5, 7], [8, 6]]),
                    'd': {'a', 'b', 'c'},
                    'e': np.array([[1, 2], [3, 4]])
                },
            })
            t1 = tree_value_clazz({
                'aa': t.a,
                'bb': np.array([[5, 6], [7, 8]]),
                'xx': {
                    'cc': t.x.c,
                    'dd': t.x.d,
                    'ee': np.array([[1, 2], [3, 4]])
                },
            })

            graph_1 = tree_value_clazz.graphics(
                (t, 't'), (t1, 't1'),
                (tree_value_clazz({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=(np.ndarray, list),
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert 4910 <= len(graph_1.source) <= 4960

            graph_2 = tree_value_clazz.graphics(
                (t, 't'), (t1, 't1'),
                (tree_value_clazz({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=False,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert 5420 <= len(graph_2.source) <= 5480

            graph_3 = tree_value_clazz.graphics(
                (t, 't'), (t1, 't1'),
                (tree_value_clazz({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=lambda x: id(x),
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert 4700 <= len(graph_3.source) <= 4760

            graph_4 = tree_value_clazz.graphics(
                (t, 't'), (t1, 't1'),
                (tree_value_clazz({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=lambda x: type(x).__name__,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert 3720 <= len(graph_4.source) <= 3780

            graph_6 = tree_value_clazz.graphics(
                (t, 't'), (t1, 't1'),
                (tree_value_clazz({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
                dup_value=True,
                title="This is a demo of 2 trees with dup value.",
                cfg={'bgcolor': '#ffffffff'},
            )
            assert 4700 <= len(graph_6.source) <= 4760

    return _TestClass
