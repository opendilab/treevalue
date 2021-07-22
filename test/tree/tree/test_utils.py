from functools import reduce
from operator import __mul__

import pytest

from treevalue.tree import jsonify, TreeValue, view, clone, typetrans, mapping, filter_, mask, union, shrink


@pytest.mark.unittest
class TestTreeTreeUtils:
    def test_jsonify(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert jsonify(tv1.c) == {'x': 2, 'y': 3}

    def test_view(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = view(tv1, ['c'])

        tv2.y = 4
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 4}
        }
        assert jsonify(tv1.c) == {'x': 2, 'y': 4}

        tv1.c = {'a': 2, 'b': 3}
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'a': 2, 'b': 3}
        }
        assert jsonify(tv1.c) == {'a': 2, 'b': 3}

    def test_clone(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = clone(tv1)

        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }

        tv1.a = 3
        tv1.b = 4
        tv1.c = {'a': 7, 'b': 4}
        assert jsonify(tv1) == {
            'a': 3, 'b': 4, 'c': {'a': 7, 'b': 4}
        }
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }

    def test_typetrans(self):
        class MyTreeValue(TreeValue):
            pass

        class NonTreeValue:
            pass

        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = typetrans(tv1, MyTreeValue)

        assert tv2 == MyTreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv2 != tv1

        with pytest.raises(TypeError):
            typetrans(tv1, NonTreeValue)

    def test_mapping(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = mapping(tv1, lambda x: x + 2)
        tv3 = mapping(tv1, lambda: 1)
        tv4 = mapping(tv1, lambda x, p: (x, p))

        assert tv2 == TreeValue({'a': 3, 'b': 4, 'c': {'x': 4, 'y': 5}})
        assert tv3 == TreeValue({'a': 1, 'b': 1, 'c': {'x': 1, 'y': 1}})
        assert tv4 == TreeValue({'a': (1, ('a',)), 'b': (2, ('b',)), 'c': {'x': (2, ('c', 'x')), 'y': (3, ('c', 'y'))}})

    def test_mask(self):
        class MyTreeValue(TreeValue):
            pass

        t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        m1 = TreeValue({'a': True, 'b': False, 'x': False})
        m2 = TreeValue({'a': True, 'b': False, 'x': {'c': True, 'd': False}})

        assert mask(t, m1) == MyTreeValue({'a': 1})
        assert mask(t, m2) == MyTreeValue({'a': 1, 'x': {'c': 3}})

    def test_union(self):
        t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        tx = mapping(t, lambda v: v % 2 == 1)
        assert union(t, tx) == TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})

        class MyTreeValue(TreeValue):
            pass

        t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert union(t, t1) == TreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})
        assert union(t1, t) == MyTreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})

    def test_filter(self):
        class MyTreeValue(TreeValue):
            pass

        t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        assert filter_(t, lambda x: x < 3) == MyTreeValue({'a': 1, 'b': 2})
        assert filter_(t, lambda x: x < 3, remove_empty=False) == MyTreeValue({'a': 1, 'b': 2, 'x': {}})
        assert filter_(t, lambda x: x % 2 == 1) == MyTreeValue({'a': 1, 'x': {'c': 3}})

    def test_shrink(self):
        class MyTreeValue(TreeValue):
            pass

        t = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert shrink(t, lambda **kwargs: sum(kwargs.values())) == 10
        assert shrink(t, lambda **kwargs: reduce(__mul__, list(kwargs.values()))) == 24

        assert shrink(t, lambda **kwargs: sum(kwargs.values()) if 'c' in kwargs.keys() else TreeValue(kwargs)) \
               == MyTreeValue({'a': 1, 'b': 2, 'x': 7})

        t.x = shrink(t.x, lambda **kwargs: sum(kwargs.values()))
        assert t == MyTreeValue({'a': 1, 'b': 2, 'x': 7})
