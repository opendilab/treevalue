import re

import pytest

from treevalue.tree.common import Tree


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
