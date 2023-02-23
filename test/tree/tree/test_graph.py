import numpy as np
import pytest

from treevalue import FastTreeValue, graphics


class MyFastTreeValue(FastTreeValue):
    pass


@pytest.mark.unittest
class TestTreeTreeGraph:
    def test_graphics(self):
        t = MyFastTreeValue({
            'a': [4, 3, 2, 1],
            'b': np.array([[5, 6], [7, 8]]),
            'x': {
                'c': np.array([[5, 7], [8, 6]]),
                'd': {'a', 'b', 'c'},
                'e': np.array([[1, 2], [3, 4]])
            },
        })
        t1 = MyFastTreeValue({
            'aa': t.a,
            'bb': np.array([[5, 6], [7, 8]]),
            'xx': {
                'cc': t.x.c,
                'dd': t.x.d,
                'ee': np.array([[1, 2], [3, 4]])
            },
        })

        graph_1 = graphics(
            (t, 't'), (t1, 't1'),
            (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
            dup_value=(np.ndarray, list),
            title="This is a demo of 2 trees with dup value.",
            cfg={'bgcolor': '#ffffffff'},
        )
        assert len(graph_1.source) <= 5000

        graph_2 = graphics(
            (t, 't'), (t1, 't1'),
            (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
            dup_value=False,
            title="This is a demo of 2 trees with dup value.",
            cfg={'bgcolor': '#ffffffff'},
        )
        assert len(graph_2.source) <= 5600

        graph_3 = graphics(
            (t, 't'), (t1, 't1'),
            (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
            dup_value=lambda x: id(x),
            title="This is a demo of 2 trees with dup value.",
            cfg={'bgcolor': '#ffffffff'},
        )
        assert len(graph_3.source) <= 4760

        graph_4 = graphics(
            (t, 't'), (t1, 't1'),
            (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
            dup_value=lambda x: type(x).__name__,
            title="This is a demo of 2 trees with dup value.",
            cfg={'bgcolor': '#ffffffff'},
        )
        assert len(graph_4.source) <= 3780

        graph_6 = graphics(
            (t, 't'), (t1, 't1'),
            (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
            dup_value=True,
            title="This is a demo of 2 trees with dup value.",
            cfg={'bgcolor': '#ffffffff'},
        )
        assert len(graph_6.source) <= 4760
