from treevalue import FastTreeValue

nt1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
nt2 = FastTreeValue({'a': 11, 'b': 24, 'x': {'c': 30, 'd': 47}})
nt3 = FastTreeValue({
    'first': nt1,
    'second': nt2,
    'another': nt1.x,
    'sum': nt1 + nt2,
})
