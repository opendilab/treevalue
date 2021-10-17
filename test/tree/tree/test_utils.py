import pytest

from treevalue.tree import TreeValue, mapping, union, raw, \
    subside, rise


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeUtils:
    def test_union(self):
        t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        tx = mapping(t, lambda v: v % 2 == 1)
        assert union(t, tx) == TreeValue({'a': (1, True), 'b': (2, False), 'x': {'c': (3, True), 'd': (4, False)}})

        class MyTreeValue(TreeValue):
            pass

        t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        assert union(t, t1) == TreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})
        assert union(t1, t) == MyTreeValue({'a': (1, 1), 'b': (2, 2), 'x': {'c': (3, 3), 'd': (4, 4)}})

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

    def test_rise(self):
        t1 = TreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6, 7], 'b': [7, 8]})})
        assert rise(t1) == {
            'a': TreeValue({'x': [1, 2], 'y': [5, 6, 7]}),
            'b': [
                TreeValue({'x': 2, 'y': 7}),
                TreeValue({'x': 3, 'y': 8}),
            ]
        }
        assert rise(TreeValue({})) == TreeValue({})
        assert rise(TreeValue({'a': 1, 'b': 2})) == TreeValue({'a': 1, 'b': 2})

        class MyTreeValue(TreeValue):
            pass

        t2 = MyTreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6, 7], 'b': [7, 8]})})
        assert rise(t2) == {
            'a': MyTreeValue({'x': [1, 2], 'y': [5, 6, 7]}),
            'b': [
                MyTreeValue({'x': 2, 'y': 7}),
                MyTreeValue({'x': 3, 'y': 8}),
            ]
        }

        t3 = MyTreeValue({'x': raw({'a': [1, 2], 'b': [2, 3]}), 'y': raw({'a': [5, 6], 'b': [7, 8]})})
        assert rise(t3) == {
            'a': [
                MyTreeValue({'x': 1, 'y': 5}),
                MyTreeValue({'x': 2, 'y': 6}),
            ],
            'b': [
                MyTreeValue({'x': 2, 'y': 7}),
                MyTreeValue({'x': 3, 'y': 8}),
            ]
        }

        t4 = MyTreeValue({'x': raw({'a': (1, 2), 'b': (2, 3)}), 'y': raw({'a': (5, 6), 'b': (7, 8)})})
        assert rise(t4) == {
            'a': (
                MyTreeValue({'x': 1, 'y': 5}),
                MyTreeValue({'x': 2, 'y': 6}),
            ),
            'b': (
                MyTreeValue({'x': 2, 'y': 7}),
                MyTreeValue({'x': 3, 'y': 8}),
            )
        }
        assert rise(t4, template={'a': (None, None), 'b': (None, None)}) == {
            'a': (
                MyTreeValue({'x': 1, 'y': 5}),
                MyTreeValue({'x': 2, 'y': 6}),
            ),
            'b': (
                MyTreeValue({'x': 2, 'y': 7}),
                MyTreeValue({'x': 3, 'y': 8}),
            )
        }
        assert rise(t4, template={'a': None, 'b': None}) == {
            'a': MyTreeValue({'x': (1, 2), 'y': (5, 6)}),
            'b': MyTreeValue({'x': (2, 3), 'y': (7, 8)}),
        }
        with pytest.raises(ValueError):
            rise(t4, template={'a': [], 'b': None})

        t5 = TreeValue({
            'x': raw([{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 5}]),
            'y': raw([{'a': 21, 'b': 32}, {'a': -2, 'b': 23}, {'a': 53, 'b': 25}]),
        })
        assert rise(t5) == [
            {'a': TreeValue({'x': 1, 'y': 21}), 'b': TreeValue({'x': 2, 'y': 32})},
            {'a': TreeValue({'x': 2, 'y': -2}), 'b': TreeValue({'x': 3, 'y': 23})},
            {'a': TreeValue({'x': 3, 'y': 53}), 'b': TreeValue({'x': 5, 'y': 25})},
        ]
        assert rise(t5, template=[{'a': None, 'b': None}]) == [
            {'a': TreeValue({'x': 1, 'y': 21}), 'b': TreeValue({'x': 2, 'y': 32})},
            {'a': TreeValue({'x': 2, 'y': -2}), 'b': TreeValue({'x': 3, 'y': 23})},
            {'a': TreeValue({'x': 3, 'y': 53}), 'b': TreeValue({'x': 5, 'y': 25})},
        ]
        assert rise(t5, template=[]) == [
            TreeValue({'x': raw({'a': 1, 'b': 2}), 'y': raw({'a': 21, 'b': 32})}),
            TreeValue({'x': raw({'a': 2, 'b': 3}), 'y': raw({'a': -2, 'b': 23})}),
            TreeValue({'x': raw({'a': 3, 'b': 5}), 'y': raw({'a': 53, 'b': 25})}),
        ]
        assert rise(t5, template=[None]) == [
            TreeValue({'x': raw({'a': 1, 'b': 2}), 'y': raw({'a': 21, 'b': 32})}),
            TreeValue({'x': raw({'a': 2, 'b': 3}), 'y': raw({'a': -2, 'b': 23})}),
            TreeValue({'x': raw({'a': 3, 'b': 5}), 'y': raw({'a': 53, 'b': 25})}),
        ]
        with pytest.raises(ValueError):
            rise(t5, template=[None, None])
