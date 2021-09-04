import os

from treevalue import FastTreeValue

if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = FastTreeValue({'a': 3, 'b': 7, 'x': {'c': 14, 'd': -5}})

    print('t1:', t1, sep=os.linesep)
    print('t2:', t2, sep=os.linesep)
    print('t1 + t2:', t1 + t2, sep=os.linesep)
    _original_ids = (id(t1), id(t2))
    print()

    t1 += t2
    print('After t1 += t2')
    print('t1:', t1, sep=os.linesep)
    print('t2:', t2, sep=os.linesep)
    assert (id(t1), id(t2)) == _original_ids
