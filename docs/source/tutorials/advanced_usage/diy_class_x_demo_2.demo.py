import os

from treevalue import general_tree_value, FastTreeValue


class AddZeroTreeValue(general_tree_value(methods=dict(
    __add__=dict(missing=0, mode='outer'),
    __radd__=dict(missing=0, mode='outer'),
    __iadd__=dict(missing=0, mode='outer'),
))):
    pass


class MulOneTreeValue(general_tree_value(methods=dict(
    __mul__=dict(missing=1, mode='outer'),
    __rmul__=dict(missing=1, mode='outer'),
    __imul__=dict(missing=1, mode='outer'),
))):
    pass


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3}})
    t2 = FastTreeValue({'a': 11, 'x': {'c': 30, 'd': 47}})

    # __add__ with default value 0
    at1 = t1.type(AddZeroTreeValue)
    at2 = t2.type(AddZeroTreeValue)
    print('at1 + at2:', at1 + at2, sep=os.linesep)

    # __mul__ with default value 1
    mt1 = t1.type(MulOneTreeValue)
    mt2 = t2.type(MulOneTreeValue)
    print('mt1 * mt2:', mt1 * mt2, sep=os.linesep)
