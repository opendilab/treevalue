import os

from treevalue import func_treelize, FastTreeValue


@func_treelize(mode='outer', missing=lambda: [])
def plus(a, b):
    return a + b


if __name__ == '__main__':
    t1 = FastTreeValue({
        'b': [2, 3],
        'x': {
            'c': [5],
            'd': [7, 11, 13],
            'e': [17, 19],
        }
    })
    t2 = FastTreeValue({
        'a': [23],
        'b': [29, 31],
        'x': {
            'c': [37],
            'd': [41, 43],
        }
    })

    print('plus(t1, t2):', plus(t1, t2), sep=os.linesep)
