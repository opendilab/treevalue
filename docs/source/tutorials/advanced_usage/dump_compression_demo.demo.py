import gzip
import os

from treevalue import FastTreeValue, dumps, loads

if __name__ == '__main__':
    t = FastTreeValue({'a': 'ab', 'b': 'Cd', 'x': {'c': 'eF', 'd': 'GH'}})
    st = t.upper
    print('st:', st, sep=os.linesep)  # st is a function tree
    print('st():', st(), sep=os.linesep)  # st() if an upper-case-string tree
    print()

    binary = dumps(st, compress=(gzip.compress, gzip.decompress))
    print('Length of binary:', len(binary))

    # compression function is not needed here
    dst = loads(binary, type_=FastTreeValue)
    print('dst:', dst, sep=os.linesep)
    assert st() == dst()  # st() should be equal to dst()
    print('dst():', dst(), sep=os.linesep)
