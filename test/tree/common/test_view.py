import pickle
import re

import pytest

from treevalue.tree.common import Tree, raw


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeCommonView:
    def test_simple_view(self):
        t = Tree({'a': 1, 'x': {'b': 233, 'c': 'sdklfgjl', 'f': {'t': 2, 'p': 3}}})

        tv1 = t.view(['x'])
        assert tv1 == Tree({'b': 233, 'c': 'sdklfgjl', 'f': {'t': 2, 'p': 3}})

        with pytest.raises(TypeError):
            tv2 = t.view(['a'])
            tv2.json()

        t['x']['b'] = 234
        assert tv1 == Tree({'b': 234, 'c': 'sdklfgjl', 'f': {'t': 2, 'p': 3}})
        assert tv1['b'] == 234

        tv1['b'] = 235
        assert t == Tree({'a': 1, 'x': {'b': 235, 'c': 'sdklfgjl', 'f': {'t': 2, 'p': 3}}})

        del tv1['c']
        assert t == Tree({'a': 1, 'x': {'b': 235, 'f': {'t': 2, 'p': 3}}})

        tv3 = tv1.clone()
        assert isinstance(tv3, Tree)
        tv1['d'] = 345
        assert tv1 == Tree({'b': 235, 'd': 345, 'f': {'t': 2, 'p': 3}})
        assert tv3 == Tree({'b': 235, 'f': {'t': 2, 'p': 3}})
        assert t == Tree({'a': 1, 'x': {'b': 235, 'd': 345, 'f': {'t': 2, 'p': 3}}})

        assert re.fullmatch(r"<TreeView 0x[0-9a-f]+ keys: \['b', 'd', 'f']>", repr(tv1))
        assert re.fullmatch(r"<Tree 0x[0-9a-f]+ keys: \['b', 'f']>", repr(tv3))

        t['x'] = {'a': 1, 'b': 2, 'c': 3, 'd': {'t': 'p', 'q': -1}}
        assert tv1 == Tree({'a': 1, 'b': 2, 'c': 3, 'd': {'t': 'p', 'q': -1}})

        tv4 = tv1.view(['d'])
        assert tv4 == Tree({'t': 'p', 'q': -1})
        t['x'] = {'a': 3, 'b': 2, 'c': 1, 'd': {'t': -1, 'q': -2}}
        assert tv4 == Tree({'t': -1, 'q': -2})

        assert set(tv4.values()) == {-1, -2}
        assert set(tv1.values()) == {
            3, 2, 1, Tree({'t': -1, 'q': -2})
        }

    def test_deep_clone(self):
        tx = Tree({
            'a': {
                'a': raw({'a': 1, 'b': 2}),
                'b': raw({'a': 3, 'b': 4}),
                'x': {
                    'c': raw({'a': 5, 'b': 6}),
                    'd': raw({'a': 7, 'b': 8}),
                }
            }
        })

        t = tx.view(['a'])

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
