import pytest

from treevalue.tree import FastTreeValue, method_treelize
from .base import get_fasttreevalue_test


class MyFastTreeValue(FastTreeValue):
    @method_treelize(missing=0, mode='outer')
    def __add__(self, other):
        return self + other

    @method_treelize(missing=0, mode='outer')
    def __radd(self, other):
        return other + self


@pytest.mark.unittest
class TestTreeGeneralFast(get_fasttreevalue_test(FastTreeValue)):
    def test_my_fast_tree_value(self):
        t1 = MyFastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 7}})
        t2 = MyFastTreeValue({'a': 11, 'b': 22, 'c': 4, 'x': {'c': 33, 'd': 5}})
        assert (t1 + t2) == MyFastTreeValue({'a': 12, 'b': 24, 'c': 4, 'x': {'c': 36, 'd': 9, 'e': 7}})

        with pytest.raises(KeyError):
            _ = t1 - t2
