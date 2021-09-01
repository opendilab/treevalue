from treevalue import FastTreeValue

t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
t2 = FastTreeValue({'a': 11, 'b': 24, 'x': {'c': 30, 'd': 47}})
t3 = t1 + t2
