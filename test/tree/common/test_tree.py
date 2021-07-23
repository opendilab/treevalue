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

    def test_tree_repr_and_len(self):
        t = Tree({'a': 1, 'x': {'b': 1, 'c': 2}})
        t1 = Tree(t)
        t1['x'] = {'b1': 1, 'b2': 2, 'b4': 5, 't': {'v': 33}}
        del t1['x']['b2']
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['a', 'x']>", repr(t))
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['a', 'x']>", repr(t1))
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['b1', 'b4', 't']>", repr(t1['x']))

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
