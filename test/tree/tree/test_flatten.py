import pytest

from treevalue.tree import TreeValue, raw, flatten, unflatten, flatten_values, flatten_keys, delayed


class MyTreeValue(TreeValue):
    pass


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeFlatten:
    def test_flatten(self):
        t = TreeValue({'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}})

        flatted = sorted(flatten(t))
        assert flatted == [
            (('a',), 1),
            (('b',), 2),
            (('c',), {'x': 3, 'y': 4}),
            (('d', 'x'), 3),
            (('d', 'y'), 4)
        ]

        t1 = TreeValue({
            'a': delayed(lambda: t.a),
            'b': delayed(lambda: t.b),
            'c': delayed(lambda: t.c),
            'd': delayed(lambda: t.d),
        })
        flatted = sorted(flatten(t1))
        assert flatted == [
            (('a',), 1),
            (('b',), 2),
            (('c',), {'x': 3, 'y': 4}),
            (('d', 'x'), 3),
            (('d', 'y'), 4)
        ]

    def test_flatten_values(self):
        t = TreeValue({'a': 1, 'b': 5, 'c': {'x': 3, 'y': 4}, 'd': {'x': 3, 'y': 4}})
        flatted_values = sorted(flatten_values(t))
        assert flatted_values == [1, 3, 3, 4, 4, 5]

        t1 = TreeValue({
            'a': delayed(lambda: t.a),
            'b': delayed(lambda: t.b),
            'c': delayed(lambda: t.c),
            'd': delayed(lambda: t.d),
        })
        flatted_values = sorted(flatten_values(t1))
        assert flatted_values == [1, 3, 3, 4, 4, 5]

    def test_flatten_keys(self):
        t = TreeValue({'a': 1, 'd': {'x': 3, 'y': 4}, 'e': raw({'x': 3, 'y': 4}), 'b': 5, 'c': {'x': 3, 'y': 4}})
        flatted_keys = sorted(flatten_keys(t))
        assert flatted_keys == [
            ('a',),
            ('b',),
            ('c', 'x',),
            ('c', 'y',),
            ('d', 'x',),
            ('d', 'y',),
            ('e',),
        ]

        t1 = TreeValue({
            'a': delayed(lambda: t.a),
            'b': delayed(lambda: t.b),
            'c': delayed(lambda: t.c),
            'd': delayed(lambda: t.d),
            'e': delayed(lambda: t.e),
        })
        flatted_keys = sorted(flatten_keys(t1))
        assert flatted_keys == [
            ('a',),
            ('b',),
            ('c', 'x',),
            ('c', 'y',),
            ('d', 'x',),
            ('d', 'y',),
            ('e',),
        ]

    def test_unflatten(self):
        flatted = [
            (('a',), 1),
            (('b',), 2),
            (('c',), {'x': 3, 'y': 4}),
            (('d', 'x'), 3),
            (('d', 'y'), 4)
        ]
        assert unflatten(flatted) == TreeValue({
            'a': 1, 'b': 2,
            'c': raw({'x': 3, 'y': 4}),
            'd': {'x': 3, 'y': 4}}
        )
        assert unflatten(flatted, MyTreeValue) == MyTreeValue({
            'a': 1, 'b': 2,
            'c': raw({'x': 3, 'y': 4}),
            'd': {'x': 3, 'y': 4}}
        )

        unordered_flatted = [
            (('a',), 1),
            (('d', 'x'), 3),
            (('b',), 2),
            (('c',), {'x': 3, 'y': 4}),
            (('d', 'y'), 4)
        ]
        assert unflatten(unordered_flatted) == TreeValue({
            'a': 1, 'b': 2,
            'c': raw({'x': 3, 'y': 4}),
            'd': {'x': 3, 'y': 4}}
        )
        assert unflatten(unordered_flatted, MyTreeValue) == MyTreeValue({
            'a': 1, 'b': 2,
            'c': raw({'x': 3, 'y': 4}),
            'd': {'x': 3, 'y': 4}}
        )
