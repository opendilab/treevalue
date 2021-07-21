import re

import pytest

from treevalue.tree.tree import TreeValue


@pytest.mark.unittest
class TestTreeTreeTree:
    def test_tree_value_init(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv1.a == 1
        assert tv1.b == 2

        tv2 = TreeValue(tv1)
        assert tv2.a == 1
        assert tv2.b == 2

        tv3 = TreeValue({'a': tv1, 'b': tv2, 'c': tv1})
        assert tv3.a.a == 1
        assert tv3.b.a == 1
        assert tv3.c.a == 1

        with pytest.raises(TypeError):
            TreeValue(1)

    def test_tree_value_operate(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = TreeValue(tv1)
        tv3 = TreeValue({'a': tv1, 'b': tv2, 'c': tv1})

        tv1.a = 3
        assert tv1.a == 3
        assert tv2.a == 3
        assert tv3.a.a == 3
        assert tv3.b.a == 3
        assert tv3.c.a == 3

        del tv1.b
        assert 'b' not in tv1
        assert 'b' not in tv2
        assert 'b' not in tv3.a
        assert 'b' not in tv3.b
        assert 'b' not in tv3.c

        with pytest.raises(KeyError):
            _ = tv1.dd

        tv1.a = {'a1': 1, 'a2': 2}
        assert tv1.a.a1 == 1
        assert tv2.a.a1 == 1
        assert tv3.a.a.a1 == 1

        tv1.a = TreeValue({'a1': 2, 'a2': 1})
        assert tv1.a.a1 == 2
        assert tv2.a.a1 == 2
        assert tv3.a.a.a1 == 2

        with pytest.raises(AttributeError):
            del tv1._property__data

    def test_tree_value_repr(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})

        assert re.fullmatch(r"<TreeValue 0x[0-9a-f]+ keys: \['a', 'b', 'c']>", repr(tv1))
        assert re.fullmatch(r"<TreeValue 0x[0-9a-f]+ keys: \['x', 'y']>", repr(tv1.c))

    def test_tree_value_iter(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert dict(tv1) == {
            'a': 1,
            'b': 2,
            'c': TreeValue({'x': 2, 'y': 3})
        }
        assert dict(tv1.c) == {
            'x': 2, 'y': 3
        }

    def test_tee_value_hash_equal(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv1 == tv1
        assert not tv1 == 2
        assert tv1 == TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv1.c == TreeValue({'x': 2, 'y': 3})

        d = {
            tv1: 1,
            tv1.c: 2
        }
        assert d[tv1] == 1
        assert d[TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})] == 1
        assert d[TreeValue({'x': 2, 'y': 3})] == 2
