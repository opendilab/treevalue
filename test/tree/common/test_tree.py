import pickle
import re

import pytest

from treevalue.tree.common import Tree, raw


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeCommonTree:
    def test_tree_init_and_eq(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        assert t == Tree({'x': {'c': 2, 'b': 1}, 'a': 1})
        assert t == t
        assert t != 233

        t1 = Tree(t)
        assert t == t1
        assert t is not t1
        assert t == t.clone()
        assert hash(t) == hash(t.clone())
        assert t is not t.clone()

        with pytest.raises(TypeError):
            Tree(233)

        t1 = Tree({'a': 1, 'x': {'b': 1, 'c': None}})
        assert t != t1
        assert hash(t) != hash(t1)
        assert t1 != Tree({'a': 1, 'x': {'b': 1, 'f': None}})

        h = {t: 1, t1: 2}
        assert h[t] == 1
        assert h[t.clone()] == 1
        assert h[Tree(t)] == 1
        assert h[t1] == 2
        assert h[Tree(t1.json())] == 2

    def test_copy_from(self):
        t1 = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        t2 = Tree({'a': 11, 'b': 24, 'x': {'b': 12, 'e': {'dfkj': 892374}}})
        original_id = id(t1.actual())
        original_id_x = id(t1['x'].actual())

        t1.copy_from(t2)
        assert t1 == t2
        assert t1 is not t2
        assert id(t1.actual()) == original_id
        assert id(t1['x'].actual()) == original_id_x
        assert t1['x']['e'] == t2['x']['e']
        assert t1['x']['e'] is not t2['x']['e']

    def test_tree_items(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        assert t['a'] == 1
        assert t['x'] == Tree({'b': 1, 'c': 2})
        with pytest.raises(KeyError):
            _ = t['233']

        t1 = Tree(t)
        t1['x'] = {'b1': 1, 'b2': 2, 'b4': 5, 't': {'v': 33}}
        assert t == Tree({'x': {'c': 2, 'b': 1}, 'a': 1})
        assert t1 == Tree({'x': {'b1': 1, 'b2': 2, 'b4': 5, 't': {'v': 33}}, 'a': 1})

        del t1['x']['b2']
        assert t == Tree({'x': {'c': 2, 'b': 1}, 'a': 1})
        assert t1 == Tree({'x': {'b1': 1, 'b4': 5, 't': {'v': 33}}, 'a': 1})

    def test_tree_str(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        assert "'a' --> 1" in str(t)
        assert "'b' --> 1" in str(t)
        assert "'c' --> 2" in str(t)

    def test_tree_repr(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        t1 = Tree(t)
        t1['x'] = {'b1': 1, 'b2': 2, 'b4': 5, 't': {'v': 33}}
        del t1['x']['b2']
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['a', 'x']>", repr(t))
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['a', 'x']>", repr(t1))
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['b1', 'b4', 't']>", repr(t1['x']))

    def test_tree_len(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        t1 = Tree(t)
        t1['x'] = {'b1': 1, 'b2': 2, 'b4': 5, 't': {'v': 33}}
        del t1['x']['b2']
        assert len(t) == 2
        assert len(t1) == 2
        assert len(t1['x']) == 3
        assert t
        assert t1
        assert not Tree({})

    def test_tree_iters(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})

        assert 'a' in t.keys()
        assert 'x' in t.keys()
        assert 't' not in t.keys()
        assert 'b' in t['x'].keys()
        assert 'xx' not in t['x'].keys()

        assert 1 in t.values()
        assert Tree({'b': 1, 'c': 2}) in t.values()
        assert Tree({'b': 1, 'c': None}) not in t.values()

        assert {key: value for key, value in t.items()} == \
               {'a': 1, 'x': Tree({'b': 1, 'c': 2})}

    def test_raw(self):
        t = Tree({
            'a': raw({'a': 1, 'b': 2}),
            'b': raw({'a': 3, 'b': 4}),
            'x': {
                'c': raw({'a': 5, 'b': 6}),
                'd': raw({'a': 7, 'b': 8}),
            }
        })

        assert t['a'] == {'a': 1, 'b': 2}
        assert t['b'] == {'a': 3, 'b': 4}
        assert t['x']['c'] == {'a': 5, 'b': 6}
        assert t['x']['d'] == {'a': 7, 'b': 8}

        t1 = t.clone()
        assert t1['a'] == {'a': 1, 'b': 2}
        assert t1['b'] == {'a': 3, 'b': 4}
        assert t1['x']['c'] == {'a': 5, 'b': 6}
        assert t1['x']['d'] == {'a': 7, 'b': 8}

        t['a'] = raw({'a': 9, 'b': 10})
        assert t['a'] == {'a': 9, 'b': 10}
        assert t['b'] == {'a': 3, 'b': 4}
        assert t['x']['c'] == {'a': 5, 'b': 6}
        assert t['x']['d'] == {'a': 7, 'b': 8}

    def test_invalid_key(self):
        with pytest.raises(KeyError):
            _ = Tree({'a': 123, '\uffff': 321})

        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        with pytest.raises(KeyError):
            t['\uffff'] = 233
        with pytest.raises(KeyError):
            t['a' * 0x1ffff] = 233
        with pytest.raises(KeyError):
            t[''] = 233
        with pytest.raises(KeyError):
            t['0'] = 233

    def test_deep_clone(self):
        t = Tree({
            'a': raw({'a': 1, 'b': 2}),
            'b': raw({'a': 3, 'b': 4}),
            'x': {
                'c': raw({'a': 5, 'b': 6}),
                'd': raw({'a': 7, 'b': 8}),
            }
        })

        t1 = t.clone()
        t2 = t.clone(copy_value=True)

        assert t1 == t
        assert t1['a'] is t['a']
        assert t1['b'] is t['b']
        assert t1['x']['c'] is t['x']['c']
        assert t1['x']['d'] is t['x']['d']

        assert t2 == t
        assert t2['a'] is not t['a']
        assert t2['b'] is not t['b']
        assert t2['x']['c'] is not t['x']['c']
        assert t2['x']['d'] is not t['x']['d']

        t3 = t.clone(copy_value=pickle)
        assert t3 == t
        assert t3['a'] is not t['a']
        assert t3['b'] is not t['b']
        assert t3['x']['c'] is not t['x']['c']
        assert t3['x']['d'] is not t['x']['d']

        t4 = t.clone(copy_value=lambda x: pickle.loads(pickle.dumps(x)))
        assert t4 == t
        assert t4['a'] is not t['a']
        assert t4['b'] is not t['b']
        assert t4['x']['c'] is not t['x']['c']
        assert t4['x']['d'] is not t['x']['d']

        t5 = t.clone(copy_value=(pickle.dumps, pickle.loads))
        assert t5 == t
        assert t5['a'] is not t['a']
        assert t5['b'] is not t['b']
        assert t5['x']['c'] is not t['x']['c']
        assert t5['x']['d'] is not t['x']['d']
