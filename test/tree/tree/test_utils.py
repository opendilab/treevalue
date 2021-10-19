import pytest

from treevalue.tree import TreeValue, raw, rise


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeUtils:
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
