import os

from treevalue import dumps, FastTreeValue, loads

if __name__ == '__main__':
    t = FastTreeValue({'a': 'ab', 'b': 'Cd', 'x': {'c': 'eF', 'd': 'GH'}})
    print('t:', t, sep=os.linesep)

    binary = dumps(t)
    dt = loads(binary, type_=FastTreeValue)

    assert dt == t
    print('dt:', dt, sep=os.linesep)
