import numpy as np

from treevalue import FastTreeValue, graphics


class MyFastTreeValue(FastTreeValue):
    pass


if __name__ == '__main__':
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

    g = graphics(
        (t, 't'), (t1, 't1'),
        (MyFastTreeValue({'a': t, 'b': t1, 'c': [1, 2], 'd': t1.xx}), 't2'),
        # Here is the dup value, with several types
        # np.ndarray and list type will use the same value node,
        # but set type is not in this tuple, so will not share the same node.
        dup_value=(np.ndarray, list),
        title="This is a demo of 2 trees with dup value.",
        cfg={'bgcolor': '#ffffff00'},
    )
    g.render('graphics_dup_value.dat.gv', format='svg')
