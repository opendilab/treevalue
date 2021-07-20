import numpy as np
import pytest

from treevalue.tree import general_tree_value, func_treelize


class TreeNumber(general_tree_value()):
    pass


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


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeGeneralGeneral:

    def test_basic_methods(self):
        t3 = TreeNumber({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})
        assert t3.json() == {'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}}

        t4 = t3.view(['x'])
        t5 = t3.x.clone()
        assert t4 == TreeNumber({'c': 38, 'd': 11})
        assert t5 == TreeNumber({'c': 38, 'd': 11})
        t3.x.c = 100
        assert t4 == TreeNumber({'c': 100, 'd': 11})
        assert t5 == TreeNumber({'c': 38, 'd': 11})

    def test_numeric_add(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (2 + t1 + t2) == TreeNumber({'a': 14, 'b': 26, 'x': {'c': 38, 'd': 11}})

    def test_numeric_sub(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (2 - t1 - t2) == TreeNumber({'a': -10, 'b': -22, 'x': {'c': -34, 'd': -7}})

    def test_numeric_mul(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (2 * t1 * t2) == TreeNumber({'a': 22, 'b': 88, 'x': {'c': 198, 'd': 40}})

    def test_numeric_matmul(self):
        t1 = TreeNumber({
            'a': np.array([[1, 2], [3, 4]]),
            'b': np.array([[2, 3], [4, 5]]),
            'x': {
                'c': np.array([[3, 4], [5, 6]]),
                'd': np.array([[4, 5], [6, 7]]),
            }
        })
        t2 = TreeNumber({
            'a': np.array([[4, 5], [6, 7]]),
            'b': np.array([[3, 4], [5, 6]]),
            'x': {
                'c': np.array([[2, 3], [4, 5]]),
                'd': np.array([[1, 2], [3, 4]]),
            }
        })

        assert func_treelize(inherit=True, return_type=TreeNumber)(np.array_equal)((t1 @ t2), TreeNumber({
            'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
            'b': np.array([[2, 3], [4, 5]]) @ np.array([[3, 4], [5, 6]]),
            'x': {
                'c': np.array([[3, 4], [5, 6]]) @ np.array([[2, 3], [4, 5]]),
                'd': np.array([[4, 5], [6, 7]]) @ np.array([[1, 2], [3, 4]]),
            }
        })) == TreeNumber({
            'a': True,
            'b': True,
            'x': {
                'c': True,
                'd': True,
            }
        })
        assert func_treelize(inherit=True, return_type=TreeNumber)(np.array_equal)(
            (t2.__rmatmul__(np.array([[1, 2], [3, 4]]))), TreeNumber({
                'a': np.array([[1, 2], [3, 4]]) @ np.array([[4, 5], [6, 7]]),
                'b': np.array([[1, 2], [3, 4]]) @ np.array([[3, 4], [5, 6]]),
                'x': {
                    'c': np.array([[1, 2], [3, 4]]) @ np.array([[2, 3], [4, 5]]),
                    'd': np.array([[1, 2], [3, 4]]) @ np.array([[1, 2], [3, 4]]),
                }
            })
        ) == TreeNumber({
            'a': True,
            'b': True,
            'x': {
                'c': True,
                'd': True,
            }
        })

    def test_numeric_floordiv(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t2 / t1) == TreeNumber({'a': 11.0, 'b': 11.0, 'x': {'c': 11.0, 'd': 1.25}})
        assert (6 / t1) == TreeNumber({'a': 6.0, 'b': 3.0, 'x': {'c': 2.0, 'd': 1.5}})

    def test_numeric_truediv(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t2 // t1) == TreeNumber({'a': 11, 'b': 11, 'x': {'c': 11, 'd': 1}})
        assert (6 // t1) == TreeNumber({'a': 6, 'b': 3, 'x': {'c': 2, 'd': 1}})

    def test_numeric_mod(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t2 % t1) == TreeNumber({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 1}})
        assert (6 % t1) == TreeNumber({'a': 0, 'b': 0, 'x': {'c': 0, 'd': 2}})

    def test_numeric_power(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert (t1 ** t1) == TreeNumber({'a': 1, 'b': 4, 'x': {'c': 27, 'd': 256}})
        assert (2 ** t1) == TreeNumber({'a': 2, 'b': 4, 'x': {'c': 8, 'd': 16}})

    def test_numeric_and(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t1 & t2) == TreeNumber({'a': 1, 'b': 2, 'x': {'c': 1, 'd': 4}})
        assert (7 & t2) == TreeNumber({'a': 3, 'b': 6, 'x': {'c': 1, 'd': 5}})

    def test_numeric_or(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t1 | t2) == TreeNumber({'a': 11, 'b': 22, 'x': {'c': 35, 'd': 5}})
        assert (7 | t2) == TreeNumber({'a': 15, 'b': 23, 'x': {'c': 39, 'd': 7}})

    def test_numeric_xor(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t1 ^ t2) == TreeNumber({'a': 10, 'b': 20, 'x': {'c': 34, 'd': 1}})
        assert (7 ^ t2) == TreeNumber({'a': 12, 'b': 17, 'x': {'c': 38, 'd': 2}})

    def test_numeric_lshift(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t2 << t1) == TreeNumber({'a': 22, 'b': 88, 'x': {'c': 264, 'd': 80}})
        assert (3 << t1) == TreeNumber({'a': 6, 'b': 12, 'x': {'c': 24, 'd': 48}})

    def test_numeric_rshift(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        assert (t2 >> t1) == TreeNumber({'a': 5, 'b': 5, 'x': {'c': 4, 'd': 0}})
        assert (32 >> t1) == TreeNumber({'a': 16, 'b': 8, 'x': {'c': 4, 'd': 2}})

    def test_numeric_pos(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert +t1 == TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

    def test_numeric_neg(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert -t1 == TreeNumber({'a': -1, 'b': -2, 'x': {'c': -3, 'd': -4}})

    def test_numeric_invert(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert ~t1 == TreeNumber({'a': -2, 'b': -3, 'x': {'c': -4, 'd': -5}})

    def test_getitem(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                         'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

        assert t2[t1 - 1] == TreeNumber({'a': 2, 'b': 13, 'x': {'c': 31, 'd': 53}})

    def test_setitem(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                         'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

        t2[t1 - 1] = t1
        assert t2 == TreeNumber({'a': [1, 3, 5, 7], 'b': [11, 2, 17, 19],
                                 'x': {'c': [23, 29, 3, 37], 'd': [41, 43, 47, 4]}})

    def test_delitem(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': [2, 3, 5, 7], 'b': [11, 13, 17, 19],
                         'x': {'c': [23, 29, 31, 37], 'd': [41, 43, 47, 53]}})

        del t2[t1 - 1]
        assert t2 == TreeNumber({'a': [3, 5, 7], 'b': [11, 17, 19],
                                 'x': {'c': [23, 29, 37], 'd': [41, 43, 47]}})

    def test_attr(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = func_treelize(inherit=True, return_type=TreeNumber)(Container)(t1)
        assert t2 == TreeNumber({'a': Container(1), 'b': Container(2), 'x': {'c': Container(3), 'd': Container(4)}})
        assert t2.value == t1

    def test_call(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = func_treelize(inherit=True, return_type=TreeNumber)(Container)(t1)
        assert t2.add(10) == TreeNumber({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
        assert t2.add(x=10) == TreeNumber({'a': 11, 'b': 12, 'x': {'c': 13, 'd': 14}})
        assert t2.add(t1) == TreeNumber({'a': 2, 'b': 4, 'x': {'c': 6, 'd': 8}})
