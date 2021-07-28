import os

from treevalue import FastTreeValue

if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = FastTreeValue({'a': 3, 'b': 7, 'x': {'c': 14, 'd': -5}})

    print("Result of t1 + t2:", t1 + t2, sep=os.linesep)  # __add__ operator
    print("Result of t1 - t2:", t1 - t2, sep=os.linesep)  # __sub__ operator
    print("Result of t1 + t2 * (-4 + t1 ** t2)", t1 + t2 * (-4 + t1 ** t2))  # mathematics calculation
