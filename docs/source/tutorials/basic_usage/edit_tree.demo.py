import os

from treevalue import FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    print("Original tree:", t, sep=os.linesep)

    # Get values
    print("Value of t.a: ", t.a)
    print("Value of t.x.c:", t.x.c)
    print("Value of t.x:", t.x, sep=os.linesep)

    # Set values
    t.a = 233
    print("Value after t.a = 233:", t, sep=os.linesep)
    t.x.d = -1
    print("Value after t.x.d = -1:", t, sep=os.linesep)
    t.x = FastTreeValue({'e': 5, 'f': 6})
    print("Value after t.x = FastTreeValue({'e': 5, 'f': 6}):", t, sep=os.linesep)
    t.x.g = {'e': 5, 'f': 6}
    print("Value after t.x.g = {'e': 5, 'f': 6}:", t, sep=os.linesep)

    # Delete values
    del t.x.g
    print("Value after del t.x.g:", t, sep=os.linesep)
