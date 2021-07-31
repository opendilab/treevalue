import numpy as np

from treevalue import FastTreeValue, graphics


class MyFastTreeValue(FastTreeValue):
    pass


if __name__ == '__main__':
    t = MyFastTreeValue({
        'a': np.array([[9, 3], [6, 4]]),
        'b': np.array([[5, 6], [7, 8]]),
        'x': {
            'c': np.array([[5, 7], [8, 6]]),
            'e': np.array([[1, 2], [3, 4]])
        },
    })
    t1 = MyFastTreeValue({
        'aa': t.a,
        'bb': np.array([[5, 6], [7, 8]]),
        'xx': {
            'cc': t.x.c,
            'ee': np.array([[1, 2], [3, 4]])
        },
    })

    g = graphics(
        (t, 't'), (t1, 't1'),
        # Here is the dup value,
        # True means lambda x: id(x), you can use your own function
        dup_value=True,
        title="This is a demo of 2 trees with dup value.",
        cfg={'bgcolor': '#ffffff00'},
    )
    g.save('graphics_dup_value.dat.gv')
    g.render(format='svg')
