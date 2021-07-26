import os

from treevalue import FastTreeValue

if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = FastTreeValue({'a': 3, 'b': 7, 'x': {'c': 14, 'd': -5}})

    print("Result of t1 + t2:", t1 + t2, sep=os.linesep)  # __add__ operator

    t3 = FastTreeValue({
        'a': [1, 2, 3],
        'b': [4, 9, 16],
        'x': {
            'c': [11, 13, 17],
            'd': [-2, -4, -8]
        }
    })
    print("Result of t3[0]:", t3[0], sep=os.linesep)  # __getitem__ operator
    print("Result of t3[::-1]:", t3[::-1], sep=os.linesep)
    print("Result of t3.x[1:]:", t3.x[1:], sep=os.linesep)
