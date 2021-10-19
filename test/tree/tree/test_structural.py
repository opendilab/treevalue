import pytest

from treevalue.tree import TreeValue, mapping, union, raw, \
    subside
import pytest

from treevalue.tree import TreeValue, mapping, union, raw, \
    subside


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeStructural:
    def test_union(self):
        t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        tx = mapping(t, lambda v: v % 2 == 1)
        assert union(t, tx) == TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})

        class MyTreeValue(TreeValue):
            pass

        t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert union(t, t1) == TreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})
        assert union(t1, t) == MyTreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})
        assert union(1, 2) == (1, 2)

    def test_subside(self):
        class MyTreeValue(TreeValue):
            pass

        original1 = {
            'a': MyTreeValue({'a': 1, 'b': 2}),
            'x': {
                'c': MyTreeValue({'a': 3, 'b': 4}),
                'd': [
                    MyTreeValue({'a': 5, 'b': 6}),
                    MyTreeValue({'a': 7, 'b': 8}),
                ]
            },
            'k': '233'
        }

        assert subside(original1) == MyTreeValue({
            'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
            'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        })
        assert subside(original1) != MyTreeValue({
            'a': {'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}},
            'b': {'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}},
        })

        original2 = {
            'a': TreeValue({'a': 1, 'b': 2}),
            'x': {
                'c': MyTreeValue({'a': 3, 'b': 4}),
                'd': [
                    MyTreeValue({'a': 5, 'b': 6}),
                    MyTreeValue({'a': 7, 'b': 8}),
                ]
            },
            'k': '233'
        }

        assert subside(original2) == TreeValue({
            'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
            'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        })
        assert subside(original2, return_type=MyTreeValue) == MyTreeValue({
            'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
            'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        })

        class MyTreeValue1(MyTreeValue):
            pass

        class MyTreeValue2(MyTreeValue):
            pass

        class MyTreeValue3(MyTreeValue):
            pass

        class MyTreeValue4(MyTreeValue):
            pass

        original3 = {
            'a': MyTreeValue1({'a': 1, 'b': 2}),
            'x': {
                'c': MyTreeValue2({'a': 3, 'b': 4}),
                'd': [
                    MyTreeValue3({'a': 5, 'b': 6}),
                    MyTreeValue4({'a': 7, 'b': 8}),
                ]
            },
            'k': '233'
        }
        assert subside(original3) == MyTreeValue({
            'a': raw({'a': 1, 'k': '233', 'x': {'c': 3, 'd': [5, 7]}}),
            'b': raw({'a': 2, 'k': '233', 'x': {'c': 4, 'd': [6, 8]}}),
        })

        assert subside({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'e': [3, 4, 5]}) == \
               {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'e': [3, 4, 5]}
