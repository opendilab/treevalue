import os

from treevalue import FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({
        'a': [1, 2, 3],
        'b': [4, 9, 16],
        'x': {
            'c': [11, 13, 17],
            'd': [-2, -4, -8]
        }
    })
    print("Result of t[0]:", t[0], sep=os.linesep)  # __getitem__ operator
    print("Result of t[::-1]:", t[::-1], sep=os.linesep)
    print("Result of t.x[1:]:", t.x[1:], sep=os.linesep)
