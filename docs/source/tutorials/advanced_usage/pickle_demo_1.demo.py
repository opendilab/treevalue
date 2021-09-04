import os
import pickle

from treevalue import TreeValue

if __name__ == '__main__':
    t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': [3, 4]}})
    binary = pickle.dumps(t)
    print('t:', t, sep=os.linesep)

    tx = pickle.loads(binary)
    assert tx == t
    print('tx:', tx, sep=os.linesep)
