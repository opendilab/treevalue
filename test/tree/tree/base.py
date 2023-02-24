import pickle
import re
from typing import Type

import pytest
from hbutils.testing import OS

from test.tree.tree.test_constraint import GreaterThanConstraint
from treevalue import raw, TreeValue, delayed, ValidationError
from treevalue.tree.common import create_storage
from treevalue.tree.tree.constraint import cleaf

try:
    _ = reversed({}.keys())
except TypeError:
    _reversible = False
else:
    _reversible = True


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


def get_treevalue_test(treevalue_class: Type[TreeValue]):
    # noinspection DuplicatedCode,PyMethodMayBeStatic

    def get_demo_constraint_tree():
        return treevalue_class({
            'a': delayed(lambda x, y: x * (y + 1), 3, 6),
            'b': delayed(lambda x: TreeValue({
                'x': f'f-{x * x!r}',
                'y': x * 1.1,
            }), x=7)
        }, constraint=[
            object,
            {
                'a': [int, GreaterThanConstraint(3)],
                'b': {
                    'x': [cleaf(), str, None],
                    'y': float,
                },
                'c': None,
            }
        ])

    # noinspection PyMethodMayBeStatic
    @pytest.mark.unittest
    class _TestClass:
        def test_tree_value_init(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert tv1.a == 1
            assert tv1.b == 2
            assert tv1.c == treevalue_class({'x': 2, 'y': 3})

            tv2 = treevalue_class(tv1)
            assert tv2.a == 1
            assert tv2.b == 2

            tv3 = treevalue_class({'a': tv1, 'b': tv2, 'c': tv1})
            assert tv3.a.a == 1
            assert tv3.b.a == 1
            assert tv3.c.a == 1

            # with usage of raw function
            tv4 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert tv4.a == 1
            assert tv4.b == 2
            assert tv4.c == treevalue_class({'x': 2, 'y': 3})
            assert tv4.c.x == 2
            assert tv4.c.y == 3
            assert tv4.d == {'x': 2, 'y': 3}
            with pytest.raises(AttributeError):  # error, tv4.d is a dict
                _ = tv4.d.x
            with pytest.raises(AttributeError):  # error, tv4.d is a dict
                _ = tv4.d.y

            with pytest.raises(TypeError):
                treevalue_class(1)

            class MyTreeValue(treevalue_class):
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
            with pytest.raises(KeyError):
                _ = tv3[0]

        def test_tree_value_operate(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            tv2 = treevalue_class(tv1)
            tv3 = treevalue_class({'a': tv1, 'b': tv2, 'c': tv1})

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

            tv1.a = treevalue_class({'a1': 1, 'a2': 2})
            assert tv1.a.a1 == 1
            assert tv2.a.a1 == 1
            assert tv3.a.a.a1 == 1

            tv1.a = treevalue_class({'a1': 2, 'a2': 1})
            assert tv1.a.a1 == 2
            assert tv2.a.a1 == 2
            assert tv3.a.a.a1 == 2

            with pytest.raises(AttributeError):
                del tv1._property__data

            tv1.ff = raw(1)
            assert tv1.ff == 1
            tv1.fff = raw({'x': 1, 'y': 2})
            assert isinstance(tv1.fff, dict)
            assert tv1.fff == {'x': 1, 'y': 2}

        # noinspection PyTypeChecker
        def test_setdefault(self):
            t = treevalue_class({})
            assert t.setdefault('a', 1) == 1
            assert t == treevalue_class({'a': 1})
            assert t.setdefault('a', 100) == 1
            assert t == treevalue_class({'a': 1})

            assert t.setdefault('f', {'a': 1, 'b': 2}) == {'a': 1, 'b': 2}
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2})})
            assert t.setdefault('f', {'y': 1, 'z': 2}) == {'a': 1, 'b': 2}
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2})})

            assert t.setdefault('c', treevalue_class({'a': 1, 'b': 2})) == treevalue_class({'a': 1, 'b': 2})
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2}), 'c': {'a': 1, 'b': 2}})
            assert t.setdefault('c', treevalue_class({'aa': 1, 'bb': 2})) == treevalue_class({'a': 1, 'b': 2})
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2}), 'c': {'a': 1, 'b': 2}})

            d = delayed(lambda: 1)
            assert t.setdefault('g', delayed(lambda x: x + 1, d)) == 2
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2}), 'c': {'a': 1, 'b': 2}, 'g': 2})
            assert t.setdefault('g', delayed(lambda x: x + 100, d)) == 2
            assert t == treevalue_class({'a': 1, 'f': raw({'a': 1, 'b': 2}), 'c': {'a': 1, 'b': 2}, 'g': 2})

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
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})

            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv1))
            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv1.c))
            assert f"'a' --> 1" in str(tv1)
            assert f"'b' --> 2" in str(tv1)
            assert f"'x' --> 2" in str(tv1)
            assert f"'y' --> 3" in str(tv1)
            assert f"'c' --> <{treevalue_class.__name__}" in str(tv1)

            tv2 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            tv2.c.z = tv2
            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv2))
            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv2.c))
            assert f"'a' --> 1" in repr(tv2)
            assert f"'b' --> 2" in repr(tv2)
            assert f"'x' --> 2" in repr(tv2)
            assert f"'y' --> 3" in repr(tv2)
            assert f"'c' --> <{treevalue_class.__name__}" in repr(tv2)
            assert "(The same address as <root>)" in repr(tv2)

            tv3 = treevalue_class({
                'a': delayed(lambda: tv1.a),
                'b': delayed(lambda: tv1.b),
                'c': delayed(lambda: tv1.c),
            })

            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv3))
            assert re.match(rf"<{treevalue_class.__name__} 0x[0-9a-f]+>", repr(tv3.c))
            assert f"'a' --> 1" in str(tv3)
            assert f"'b' --> 2" in str(tv3)
            assert f"'x' --> 2" in str(tv3)
            assert f"'y' --> 3" in str(tv3)
            assert f"'c' --> <{treevalue_class.__name__}" in str(tv3)

        def test_tree_value_iter(self):
            # Attention: dict(tv1) is not supported in python 3.7+
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert sorted(list(tv1)) == ['a', 'b', 'c']
            assert sorted(list(tv1.c)) == ['x', 'y']

        def test_tree_value_reversed(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            if _reversible:
                assert list(reversed(tv1)) == list(iter(tv1))[::-1]
                assert list(reversed(tv1.c)) == list(iter(tv1.c))[::-1]
            else:
                with pytest.raises(TypeError):
                    reversed(tv1)
                with pytest.raises(TypeError):
                    reversed(tv1.c)

        def test_tree_value_len(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            tv2 = treevalue_class({'a': 1, 'b': 2, 'c': {}, 'd': 4})

            assert len(tv1) == 3
            assert len(tv1.c) == 2
            assert len(tv2) == 4
            assert len(tv2.c) == 0

        def test_tree_value_bool(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            tv2 = treevalue_class({'a': 1, 'b': 2, 'c': {}, 'd': 4})

            assert tv1
            assert tv1.c
            assert tv2
            assert not tv2.c

        def test_tree_value_hash_equal(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert tv1 == tv1
            assert not tv1 == 2
            assert tv1 == treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert tv1 != treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 4}})
            assert tv1.c == treevalue_class({'x': 2, 'y': 3})
            assert tv1.c != treevalue_class({'x': 2, 'y': 3, 'z': 4})

            d = {
                tv1: 1,
                tv1.c: 2
            }
            assert d[tv1] == 1
            assert d[treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})] == 1
            assert d[treevalue_class({'x': 2, 'y': 3})] == 2

        def test_serialize_support(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            bt1 = pickle.dumps(tv1)
            assert pickle.loads(bt1) == tv1

            tv2 = treevalue_class({
                'a': _Container(1),
                'b': _Container(2),
                'x': {
                    'c': _Container(3),
                    'd': _Container(4),
                }
            })
            bt2 = pickle.dumps(tv2)
            assert pickle.loads(bt2) == tv2

        # noinspection PyTypeChecker
        def test_get(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})

            assert tv1.get('a') == 1
            assert tv1.get('b') == 2
            assert tv1.get('c') == treevalue_class({'x': 2, 'y': 3})
            assert tv1.get('d') == {'x': 2, 'y': 3}
            assert tv1.get('e') is None
            assert tv1.get('e', 233) == 233

            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv2 = treevalue_class({
                'a': delayed(lambda: tv1.a),
                'b': delayed(lambda: tv1.b),
                'c': delayed(lambda: tv1.c),
            })
            assert tv2.get('a') == 1
            assert tv2.get('b') == 2
            assert tv2.get('c') == treevalue_class({'x': 2, 'y': 3})

        # noinspection PyTypeChecker
        def test_pop(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})

            assert tv1.pop('a') == 1
            with pytest.raises(KeyError):
                _ = tv1.pop('a')
            assert tv1.pop('a', 233) == 233

            assert tv1.pop('b') == 2
            assert tv1.pop('c') == treevalue_class({'x': 2, 'y': 3})
            assert tv1.pop('d') == {'x': 2, 'y': 3}
            with pytest.raises(KeyError):
                _ = tv1.pop('e')
            assert tv1.pop('e', 233) == 233

            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv2 = treevalue_class({
                'a': delayed(lambda: tv1.a),
                'b': delayed(lambda: tv1.b),
                'c': delayed(lambda: tv1.c),
            })
            assert tv2.pop('a') == 1
            assert tv2.pop('b') == 2
            assert tv2.pop('c') == treevalue_class({'x': 2, 'y': 3})

            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv3 = treevalue_class({'a': 233, 'b': tv1, 'c': tv1})
            assert tv3.pop('b') == tv1
            assert tv3.pop('c') == tv1
            with pytest.raises(KeyError):
                tv3.pop('b')
            with pytest.raises(KeyError):
                tv3.pop('c')
            assert tv3.pop('b', 345) == 345
            assert tv3.pop('c', 345) == 345

        def test_popitem(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert sorted([tv1.popitem() for _ in range(len(tv1))]) == [
                ('a', 1), ('b', 2),
                ('c', treevalue_class({'x': 2, 'y': 3})),
                ('d', {'x': 2, 'y': 3}),
            ]
            with pytest.raises(KeyError):
                tv1.popitem()

            d1 = delayed(lambda: 1)
            d2 = delayed(lambda x: x + 1, d1)
            tv2 = treevalue_class({'a': d1, 'b': d2, 'c': d1, 'd': 100})
            assert sorted([tv2.popitem() for _ in range(len(tv2))]) == [
                ('a', 1), ('b', 2), ('c', 1), ('d', 100),
            ]
            with pytest.raises(KeyError):
                tv2.popitem()

        def test_clear(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert tv1.clear() is None
            assert not tv1

        # noinspection DuplicatedCode
        def test_update(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv1.update({'a': 3, 'c': treevalue_class({'x': 3, 'y': 4}), 'd': {'x': 200, 'y': 300}})
            assert tv1 == treevalue_class({
                'a': 3, 'b': 2,
                'c': {'x': 3, 'y': 4},
                'd': raw({'x': 200, 'y': 300}),
            })

            tv2 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv2.update(a=3, c=treevalue_class({'x': 3, 'y': 4}), d={'x': 200, 'y': 300})
            assert tv2 == treevalue_class({
                'a': 3, 'b': 2,
                'c': {'x': 3, 'y': 4},
                'd': raw({'x': 200, 'y': 300}),
            })

            tv3 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv3.update(treevalue_class({'a': 3, 'c': {'x': 3, 'y': 4}, 'd': raw({'x': 200, 'y': 300})}))
            assert tv3 == treevalue_class({
                'a': 3, 'b': 2,
                'c': {'x': 3, 'y': 4},
                'd': raw({'x': 200, 'y': 300}),
            })

            tv4 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            # noinspection PyTypeChecker
            tv4.update(create_storage({'a': 3, 'c': {'x': 3, 'y': 4}, 'd': raw({'x': 200, 'y': 300})}))
            assert tv4 == treevalue_class({
                'a': 3, 'b': 2,
                'c': {'x': 3, 'y': 4},
                'd': raw({'x': 200, 'y': 300}),
            })

            tv5 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            with pytest.raises(TypeError):
                tv5.update('sdklfj')
            with pytest.raises(TypeError):
                tv5.update(123)

            tv6 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            tv6.update({'a': 3, 'c': treevalue_class({'x': 3, 'y': 4}), 'd': {'x': 200, 'y': 300}}, a=50, f='dfkl')
            assert tv6 == treevalue_class({
                'a': 50, 'b': 2, 'f': 'dfkl',
                'c': {'x': 3, 'y': 4},
                'd': raw({'x': 200, 'y': 300}),
            })

        def test_keys(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert len(tv1.keys()) == 4
            assert set(tv1.keys()) == {'a', 'b', 'c', 'd'}
            assert 'a' in tv1.keys()
            assert 'b' in tv1.keys()
            assert 'c' in tv1.keys()
            assert 'd' in tv1.keys()
            assert 'e' not in tv1.keys()

            assert repr(tv1.keys()) == "treevalue_keys(['a', 'b', 'c', 'd'])"
            if _reversible:
                assert list(reversed(tv1.keys())) == list(tv1.keys())[::-1]
            else:
                with pytest.raises(TypeError):
                    reversed(tv1.keys())

        def test_values(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
            assert len(tv1.values()) == 3
            assert set(tv1.c.values()) == {2, 3}
            assert 1 in tv1.values()
            assert 2 in tv1.values()
            assert 3 not in tv1.values()
            assert treevalue_class({'x': 2, 'y': 3}) in tv1.values()
            assert treevalue_class({'x': 2, 'y': 4}) not in tv1.values()

            assert repr(treevalue_class({'a': 1, 'b': 2}).values()) == 'treevalue_values([1, 2])'
            if _reversible:
                assert list(reversed(tv1.values())) == list(tv1.values())[::-1]
            else:
                with pytest.raises(TypeError):
                    reversed(tv1.values())

        def test_items(self):
            tv1 = treevalue_class({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert len(tv1.items()) == 4
            assert sorted(tv1.items()) == [
                ('a', 1),
                ('b', 2),
                ('c', treevalue_class({'x': 2, 'y': 3})),
                ('d', {'x': 2, 'y': 3}),
            ]
            assert ('a', 1) in tv1.items()
            assert ('b', 2) in tv1.items()
            assert ('a', 2) not in tv1.items()
            assert ('c', treevalue_class({'x': 2, 'y': 3})) in tv1.items()
            assert ('c', treevalue_class({'x': 2, 'y': 4})) not in tv1.items()
            assert ('d', {'x': 2, 'y': 3}) in tv1.items()
            assert ('d', {'x': 2, 'y': 4}) not in tv1.items()

            assert repr(treevalue_class({'a': 1, 'b': 2}).items()) == "treevalue_items([('a', 1), ('b', 2)])"
            if _reversible:
                assert list(reversed(tv1.items())) == list(tv1.items())[::-1]
            else:
                with pytest.raises(TypeError):
                    reversed(tv1.items())

            class MyTreeValue(treevalue_class):
                pass

            tv2 = MyTreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}, 'd': raw({'x': 2, 'y': 3})})
            assert sorted(tv2.items()) == [
                ('a', 1),
                ('b', 2),
                ('c', MyTreeValue({'x': 2, 'y': 3})),
                ('d', {'x': 2, 'y': 3}),
            ]

        def test_validation(self):
            t1 = treevalue_class({
                'a': delayed(lambda x, y: x * (y + 1), 3, 6),
                'b': delayed(lambda x: TreeValue({
                    'x': f'f-{x * x!r}',
                    'y': x * 1.1,
                    'z': None,
                }), x=7)
            }, constraint=[
                object,
                {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {
                        'x': [cleaf(), str, None],
                        'y': float,
                    },
                    'c': None,
                }
            ])
            t1.validate()

            t2 = treevalue_class({
                'a': delayed(lambda x, y: x * (y + 1), 3, 6),
                'b': delayed(lambda x: TreeValue({
                    'x': f'f-{x * x!r}',
                    'y': x * 1,
                }), x=7)
            }, constraint=[
                object,
                {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {
                        'x': [cleaf(), str, None],
                        'y': float,
                    },
                    'c': None,
                }
            ])
            with pytest.raises(ValidationError) as ei:
                t2.validate()
            err = ei.value
            self_, reterr, retpath, retcons = err.args
            assert self_ == treevalue_class({'a': 21, 'b': {'x': 'f-49', 'y': 7}})
            assert isinstance(reterr, TypeError)
            assert retpath == ('b', 'y')
            assert retcons == float
            line1, *_ = str(err).splitlines(keepends=False)
            assert line1 == "Validation failed on <TypeConstraint <class 'float'>> at position ('b', 'y')"

            t3 = treevalue_class({
                'a': delayed(lambda x, y: x * (y + 1), 3, 6),
                'b': delayed(lambda x: TreeValue({
                    'x': f'f-{x * x!r}',
                    'y': x * 1,
                }), x=7)
            })
            t3 = treevalue_class(t3, constraint=[
                object,
                {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {
                        'x': [cleaf(), str, None],
                        'y': float,
                    },
                    'c': None,
                }
            ])
            with pytest.raises(ValidationError) as ei:
                t3.validate()
            err = ei.value
            self_, reterr, retpath, retcons = err.args
            assert self_ == treevalue_class({'a': 21, 'b': {'x': 'f-49', 'y': 7}})
            assert isinstance(reterr, TypeError)
            assert retpath == ('b', 'y')
            assert retcons == float
            line1, *_ = str(err).splitlines(keepends=False)
            assert line1 == "Validation failed on <TypeConstraint <class 'float'>> at position ('b', 'y')"

        def test_constraint_get(self, ):
            t1 = get_demo_constraint_tree()
            assert t1.constraint.equiv([
                object, {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {'x': [cleaf(), str], 'y': float}
                }
            ])

            assert t1.a == 21
            t1b = t1.b
            assert t1b.x == 'f-49'
            assert t1b.y == pytest.approx(7.7)
            assert t1b.constraint.equiv([object, {'x': [cleaf(), str], 'y': float}])

            t1b = t1.get('b')
            assert t1b.x == 'f-49'
            assert t1b.y == pytest.approx(7.7)
            assert t1b.constraint.equiv([object, {'x': [cleaf(), str], 'y': float}])

            t1b = t1['b']
            assert t1b.x == 'f-49'
            assert t1b.y == pytest.approx(7.7)
            assert t1b.constraint.equiv([object, {'x': [cleaf(), str], 'y': float}])

        # noinspection PyTypeChecker
        def test_constraint_pop(self):
            t1 = get_demo_constraint_tree()
            assert t1.constraint.equiv([
                object, {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {'x': [cleaf(), str], 'y': float}
                }
            ])

            assert t1.pop('a') == 21
            assert 'a' not in t1

            t1b = t1.pop('b')
            assert 'b' not in t1
            assert t1b.x == 'f-49'
            assert t1b.y == pytest.approx(7.7)
            assert t1b.constraint.equiv([object, {'x': [cleaf(), str], 'y': float}])

        def test_constraint_popitem(self):
            t1 = get_demo_constraint_tree()

            a_found, b_found = False, False
            while t1:
                key, value = t1.popitem()
                if key == 'a':
                    assert not a_found, f'Duplicate key {"a"!r} found.'
                    assert value == 21
                    a_found = True
                elif key == 'b':
                    assert not b_found, f'Duplicate key {"b"!r} found.'
                    assert value.x == 'f-49'
                    assert value.y == pytest.approx(7.7)
                    assert value.constraint.equiv([object, {'x': [cleaf(), str], 'y': float}])
                    b_found = True
                else:
                    pytest.fail(f'Unexpected key {key!r} found.')

            assert a_found and b_found, f'Key {"a"!r} or {"b"!r} not found in {t1!r}.'

        def test_with_constraints(self):
            t1 = get_demo_constraint_tree()
            t2 = t1.with_constraints(GreaterThanConstraint(10))
            assert t2.constraint.equiv([
                GreaterThanConstraint(10),
                object,
                {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {'x': [cleaf(), str], 'y': float}
                }
            ])

            t3 = t1.with_constraints([GreaterThanConstraint(10), int], clear=True)
            assert t3.constraint.equiv([int, GreaterThanConstraint(10)])

        def test_pickle_constraints(self):
            t1 = get_demo_constraint_tree()
            assert t1.a == 21
            assert t1.b.x == 'f-49'
            assert t1.b.y == pytest.approx(7.7)
            assert t1.constraint.equiv([
                object, {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {'x': [cleaf(), str], 'y': float}
                }
            ])

            binary = pickle.dumps(t1)
            newt1 = pickle.loads(binary)
            assert newt1.a == 21
            assert newt1.b.x == 'f-49'
            assert newt1.b.y == pytest.approx(7.7)
            assert newt1.constraint.equiv([
                object, {
                    'a': [int, GreaterThanConstraint(3)],
                    'b': {'x': [cleaf(), str], 'y': float}
                }
            ])

            assert newt1 == t1
            assert newt1.constraint == t1.constraint

        def test_repr_svg(self):
            t1 = get_demo_constraint_tree()
            assert hasattr(t1, '_repr_svg_')

            _repr_svg_ = t1._repr_svg_()
            assert isinstance(_repr_svg_, str)
            assert 4500 <= len(_repr_svg_) <= 4900

        def test_repr_png(self):
            t1 = get_demo_constraint_tree()
            assert hasattr(t1, '_repr_png_')

            _repr_png_ = t1._repr_png_()
            assert isinstance(_repr_png_, bytes)
            if OS.windows:
                print(len(_repr_png_))
            assert 16050 <= len(_repr_png_) <= 20500

        def test_repr_jpeg(self):
            t1 = get_demo_constraint_tree()
            assert hasattr(t1, '_repr_jpeg_')

            _repr_jpeg_ = t1._repr_jpeg_()
            assert isinstance(_repr_jpeg_, bytes)
            assert 10500 <= len(_repr_jpeg_) <= 14500

    return _TestClass
