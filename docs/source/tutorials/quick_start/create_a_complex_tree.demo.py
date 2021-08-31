from treevalue import FastTreeValue

t1 = FastTreeValue({'a': 's1', 'b': 2, 'x': {'c': 3, 'd': [1, 2]}})
t2 = FastTreeValue({'a': 'str11', 'b': 2, 'x': {'c': 33, 'd': t1.x.d}})
t3 = FastTreeValue({'t1': t1, 't2': t2, 'sum': t1 + t2})

if __name__ == '__main__':
    print('t1:')
    print(t1)

    print('t2:')
    print(t2)

    print('t3:')
    print(t3)
