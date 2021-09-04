import numpy as np

from treevalue import FastTreeValue, graphics, TreeValue


class MyFastTreeValue(FastTreeValue):
    pass


if __name__ == '__main__':
    t = MyFastTreeValue({
        'a': 1,
        'b': np.array([[5, 6], [7, 8]]),
        'x': {
            'c': 3,
            'd': 4,
            'e': np.array([[1, 2], [3, 4]])
        },
    })
    t2 = TreeValue({'ppp': t.x, 'x': {'t': t, 'y': t.x}})

    g = graphics(
        (t, 't'), (t2, 't2'),
        title="This is a demo of 2 trees.",
        cfg={'bgcolor': '#ffffff00'},
    )
    g.render('graphics.dat.gv', format='svg')
