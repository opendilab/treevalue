import pickle
import re

import pytest

from treevalue import raw, TreeValue, delayed


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
        assert tv1.c == TreeValue({'x': 2, 'y': 3})

        tv2 = TreeValue(tv1)
        assert tv2.a == 1
        assert tv2.b == 2

        tv3 = TreeValue({'a': tv1, 'b': tv2, 'c': tv1})
        assert tv3.a.a == 1
        assert tv3.b.a == 1
        assert tv3.c.a == 1

        # with usage of raw function
        tv4 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        assert tv4.a == 1
        assert tv4.b == 2
        assert tv4.c == TreeValue({'x': 2, 'y': 3})
        assert tv4.c.x == 2
        assert tv4.c.y == 3
        assert tv4.d == {'x': 2, 'y': 3}
        with pytest.raises(AttributeError):  # error, tv4.d is a dict
            _ = tv4.d.x
        with pytest.raises(AttributeError):  # error, tv4.d is a dict
            _ = tv4.d.y

        with pytest.raises(TypeError):
            TreeValue(1)

        class MyTreeValue(TreeValue):
            pass

        tv4 = MyTreeValue({'a': tv1.c, 'x': {'b': tv1, 'c': tv2.c}})
        assert isinstance(tv4.a, MyTreeValue)
        assert isinstance(tv4.x, MyTreeValue)
        assert isinstance(tv4.x.b, MyTreeValue)
        assert isinstance(tv4.x.c, MyTreeValue)

        tv5 = MyTreeValue({'a': tv1.c, 'x': {'b': tv1._detach(), 'c': tv2.c}})
        assert isinstance(tv5.a, MyTreeValue)
        assert isinstance(tv5.x, MyTreeValue)
        assert isinstance(tv5.x.b, MyTreeValue)
        assert isinstance(tv5.x.c, MyTreeValue)

    def test_tree_value_init_with_item(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv1['a'] == 1
        assert tv1['b'] == 2

        tv2 = TreeValue(tv1)
        assert tv2['a'] == 1
        assert tv2['b'] == 2

        tv3 = TreeValue({'a': tv1, 'b': tv2, 'c': tv1})
        assert tv3['a']['a'] == 1
        assert tv3['b']['a'] == 1
        assert tv3['c']['a'] == 1

        with pytest.raises(KeyError):
            _ = tv3['g']
        with pytest.raises(KeyError):
            _ = tv3[0]

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

        with pytest.raises(AttributeError):
            _ = tv1.dd

        tv1.a = TreeValue({'a1': 1, 'a2': 2})
        assert tv1.a.a1 == 1
        assert tv2.a.a1 == 1
        assert tv3.a.a.a1 == 1

        tv1.a = TreeValue({'a1': 2, 'a2': 1})
        assert tv1.a.a1 == 2
        assert tv2.a.a1 == 2
        assert tv3.a.a.a1 == 2

        with pytest.raises(AttributeError):
            del tv1._property__data

    def test_tree_value_operate_with_item(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = TreeValue(tv1)
        tv3 = TreeValue({'a': tv1, 'b': tv2, 'c': tv1})
        tv4 = TreeValue({'a': raw({'a': 1, 'y': 2}), 'c': {'x': raw({'a': 3, 'y': 4}), }})

        tv1['a'] = 3
        assert tv1.a == 3
        assert tv2.a == 3
        assert tv3.a.a == 3
        assert tv3.b.a == 3
        assert tv3.c.a == 3

        assert tv4['a'] == {'a': 1, 'y': 2}
        assert tv4['c'] == TreeValue({'x': raw({'a': 3, 'y': 4})})
        with pytest.raises(KeyError):
            _ = tv4['y']
        with pytest.raises(KeyError):
            _ = tv4[['c']]

        tv1['f'] = 333
        assert tv1.f == 333
        assert tv1['f'] == 333
        assert 'f' in tv1

        with pytest.raises(NotImplementedError):
            tv1[0] = 3
        with pytest.raises(NotImplementedError):
            tv1[['c']] = 3

        del tv1['b']
        assert 'b' not in tv1
        assert 'b' not in tv2
        assert 'b' not in tv3.a
        assert 'b' not in tv3.b
        assert 'b' not in tv3.c

        with pytest.raises(KeyError):
            del tv1['g']
        with pytest.raises(KeyError):
            del tv1[['c']]
        with pytest.raises(KeyError):
            del tv1[0]

    def test_tree_value_repr(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})

        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv1))
        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv1.c))
        assert "'a' --> 1" in str(tv1)
        assert "'b' --> 2" in str(tv1)
        assert "'x' --> 2" in str(tv1)
        assert "'y' --> 3" in str(tv1)
        assert "'c' --> <TreeValue" in str(tv1)

        tv2 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2.c.z = tv2
        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv2))
        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv2.c))
        assert "'a' --> 1" in repr(tv2)
        assert "'b' --> 2" in repr(tv2)
        assert "'x' --> 2" in repr(tv2)
        assert "'y' --> 3" in repr(tv2)
        assert "'c' --> <TreeValue" in repr(tv2)
        assert "(The same address as <root>)" in repr(tv2)

        tv3 = TreeValue({
            'a': delayed(lambda: tv1.a),
            'b': delayed(lambda: tv1.b),
            'c': delayed(lambda: tv1.c),
        })

        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv3))
        assert re.match(r"<TreeValue 0x[0-9a-f]+>", repr(tv3.c))
        assert "'a' --> 1" in str(tv3)
        assert "'b' --> 2" in str(tv3)
        assert "'x' --> 2" in str(tv3)
        assert "'y' --> 3" in str(tv3)
        assert "'c' --> <TreeValue" in str(tv3)

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

    def test_get(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})

        assert tv1.get('a') == 1
        assert tv1.get('b') == 2
        assert tv1.get('c') == TreeValue({'x': 2, 'y': 3})
        assert tv1.get('d') == {'x': 2, 'y': 3}
        with pytest.raises(KeyError):
            _ = tv1.get('e')
        assert tv1.get('e', 233) == 233

        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        tv2 = TreeValue({
            'a': delayed(lambda: tv1.a),
            'b': delayed(lambda: tv1.b),
            'c': delayed(lambda: tv1.c),
        })
        assert tv2.get('a') == 1
        assert tv2.get('b') == 2
        assert tv2.get('c') == TreeValue({'x': 2, 'y': 3})

    def test_pop(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})

        assert tv1.pop('a') == 1
        with pytest.raises(KeyError):
            _ = tv1.pop('a')
        assert tv1.pop('a', 233) == 233

        assert tv1.pop('b') == 2
        assert tv1.pop('c') == TreeValue({'x': 2, 'y': 3})
        assert tv1.pop('d') == {'x': 2, 'y': 3}
        with pytest.raises(KeyError):
            _ = tv1.pop('e')
        assert tv1.pop('e', 233) == 233

        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        tv2 = TreeValue({
            'a': delayed(lambda: tv1.a),
            'b': delayed(lambda: tv1.b),
            'c': delayed(lambda: tv1.c),
        })
        assert tv2.pop('a') == 1
        assert tv2.pop('b') == 2
        assert tv2.pop('c') == TreeValue({'x': 2, 'y': 3})

    def test_keys(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        assert set(tv1.keys()) == {'a', 'b', 'c', 'd'}

    def test_values(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert set(tv1.c.values()) == {2, 3}
        assert len(list(tv1.values())) == 3
        assert 1 in tv1.values()
        assert 2 in tv1.values()

    def test_items(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        assert sorted(tv1.items()) == [
            ('a', 1),
            ('b', 2),
            ('c', TreeValue({'x': 2, 'y': 3})),
            ('d', {'x': 2, 'y': 3}),
        ]

        class MyTreeValue(TreeValue):
            pass

        tv2 = MyTreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
        assert sorted(tv2.items()) == [
            ('a', 1),
            ('b', 2),
            ('c', MyTreeValue({'x': 2, 'y': 3})),
            ('d', {'x': 2, 'y': 3}),
        ]
