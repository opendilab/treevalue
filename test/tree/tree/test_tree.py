import pickle
import re

import pytest

from treevalue.tree.tree import TreeValue
from treevalue.tree.tree.tree import get_data_property


class _Container:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __repr__(self):
        return '<{cls} {id} value: {value}>'.format(
            cls=self.__class__.__name__, id=hex(id(self)), value=repr(self.__value))

    def __eq__(self, other):
        if other is self:
            return True
        elif type(other) == _Container:
            return other.__value == self.value
        else:
            return False

    def __hash__(self):
        return hash((self.__value,))


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

        class MyTreeValue(TreeValue):
            pass

        tv4 = MyTreeValue({'a': tv1.c, 'x': {'b': tv1, 'c': tv2.c}})
        assert isinstance(tv4.a, MyTreeValue)
        assert isinstance(tv4.x, MyTreeValue)
        assert isinstance(tv4.x.b, MyTreeValue)
        assert isinstance(tv4.x.c, MyTreeValue)

        tv5 = MyTreeValue({'a': tv1.c, 'x': {'b': get_data_property(tv1), 'c': tv2.c}})
        assert isinstance(tv5.a, MyTreeValue)
        assert isinstance(tv5.x, MyTreeValue)
        assert isinstance(tv5.x.b, MyTreeValue)
        assert isinstance(tv5.x.c, MyTreeValue)

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

    def test_tree_value_str(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert "'a' --> 1" in str(tv1)
        assert "'b' --> 2" in str(tv1)
        assert "'x' --> 2" in str(tv1)
        assert "'y' --> 3" in str(tv1)
        assert "'c' --> <TreeValue" in str(tv1)

    def test_tree_value_iter(self):
        # Attention: dict(tv1) is not supported in python 3.7+
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert sorted(list(tv1)) == [
            ('a', 1),
            ('b', 2),
            ('c', TreeValue({'x': 2, 'y': 3}))
        ]
        assert sorted(list(tv1.c)) == [('x', 2), ('y', 3)]

    def test_tree_value_len(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = TreeValue({'a': 1, 'b': 2, 'c': {}, 'd': 4})

        assert len(tv1) == 3
        assert len(tv1.c) == 2
        assert len(tv2) == 4
        assert len(tv2.c) == 0

    def test_tree_value_bool(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = TreeValue({'a': 1, 'b': 2, 'c': {}, 'd': 4})

        assert tv1
        assert tv1.c
        assert tv2
        assert not tv2.c

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

    def test_serialize_support(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        bt1 = pickle.dumps(tv1)
        assert pickle.loads(bt1) == tv1

        tv2 = TreeValue({
            'a': _Container(1),
            'b': _Container(2),
            'x': {
                'c': _Container(3),
                'd': _Container(4),
            }
        })
        bt2 = pickle.dumps(tv2)
        assert pickle.loads(bt2) == tv2
