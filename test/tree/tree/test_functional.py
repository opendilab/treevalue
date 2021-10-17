import pytest

from treevalue.tree import TreeValue, mapping, raw


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
