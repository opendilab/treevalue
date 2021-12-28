from functools import reduce
from operator import __mul__

import pytest

from treevalue.tree import TreeValue, mapping, raw, mask, filter_, reduce_, delayed


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeFunctional:
    def test_mapping(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = mapping(tv1, lambda x: x + 2)
        tv3 = mapping(tv1, lambda: 1)
        tv4 = mapping(tv1, lambda x, p: (x, p))
        tv5 = mapping(tv1, lambda x, p: {'a': x ** (len(p) + 1), 'b': len(p) ** x})
        tv6 = mapping(tv1, float)

        assert tv2 == TreeValue({'a': 3, 'b': 4, 'c': {'x': 4, 'y': 5}})
        assert tv3 == TreeValue({'a': 1, 'b': 1, 'c': {'x': 1, 'y': 1}})
        assert tv4 == TreeValue({'a': (1, ('a',)), 'b': (2, ('b',)), 'c': {'x': (2, ('c', 'x')), 'y': (3, ('c', 'y'))}})
        assert tv5 == TreeValue({
            'a': raw({'a': 1, 'b': 1}),
            'b': raw({'a': 4, 'b': 1}),
            'c': {
                'x': raw({'a': 8, 'b': 4}),
                'y': raw({'a': 27, 'b': 8})
            }
        })
        assert tv6 == TreeValue({'a': 1.0, 'b': 2.0, 'c': {'x': 2.0, 'y': 3.0}})

        tv8 = TreeValue({'v': delayed(lambda: tv1)})
        assert mapping(tv8, lambda x: x + 2) == TreeValue({'v': {
            'a': 3, 'b': 4, 'c': {'x': 4, 'y': 5}
        }})

    def test_mask(self):
        class MyTreeValue(TreeValue):
            pass

        t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        m1 = TreeValue({'a': True, 'b': False, 'x': False})
        m2 = TreeValue({'a': True, 'b': False, 'x': {'c': True, 'd': False}})

        assert mask(t, m1) == MyTreeValue({'a': 1})
        assert mask(t, m2) == MyTreeValue({'a': 1, 'x': {'c': 3}})

        t2 = MyTreeValue({'a': 1, 'b': 2, 'x': 5})
        assert mask(t2, m1) == MyTreeValue({'a': 1})
        with pytest.raises(TypeError):
            assert mask(t2, m2)

        t1 = TreeValue({'v': delayed(lambda: t)})
        m11 = TreeValue({'v': delayed(lambda: m1)})
        assert mask(t1, m11) == TreeValue({'v': {'a': 1}})

    def test_filter(self):
        class MyTreeValue(TreeValue):
            pass

        t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        assert filter_(t, lambda x: x < 3) == MyTreeValue({'a': 1, 'b': 2})
        assert filter_(t, lambda x: x < 3, remove_empty=False) == MyTreeValue({'a': 1, 'b': 2, 'x': {}})
        assert filter_(t, lambda x: x % 2 == 1) == MyTreeValue({'a': 1, 'x': {'c': 3}})

        t2 = TreeValue({'v': delayed(lambda: t)})
        assert filter_(t2, lambda x: x < 3) == TreeValue({'v': {'a': 1, 'b': 2}})

    def test_reduce(self):
        class MyTreeValue(TreeValue):
            pass

        t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert reduce_(t1, lambda **kwargs: sum(kwargs.values())) == 10
        assert reduce_(t1, lambda **kwargs: reduce(__mul__, list(kwargs.values()))) == 24

        assert reduce_(t1, lambda **kwargs: sum(kwargs.values()) if 'c' in kwargs.keys() else TreeValue(kwargs)) \
               == MyTreeValue({'a': 1, 'b': 2, 'x': 7})

        t1.x = reduce_(t1.x, lambda **kwargs: sum(kwargs.values()))
        assert t1 == MyTreeValue({'a': 1, 'b': 2, 'x': 7})

        t2 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert reduce_(t2, lambda **kwargs: TreeValue(
            {k + k: (v ** 2 if not isinstance(v, TreeValue) else v) for k, v in kwargs.items()})) == MyTreeValue(
            {'aa': 1, 'bb': 4, 'xx': {'cc': 9, 'dd': 16}})

        t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t3 = TreeValue({'v': delayed(lambda: t1), 'v2': delayed(lambda: t1)})
        assert reduce_(t3, lambda **kwargs: sum(kwargs.values())) == 20
        assert reduce_(t3, lambda **kwargs: reduce(__mul__, list(kwargs.values()))) == 576
