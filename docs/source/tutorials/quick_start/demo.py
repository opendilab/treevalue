from treevalue import FastTreeValue

t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': [1, 2]}})
t2 = FastTreeValue({'a': 11, 'b': 2, 'x': {'c': 33, 'd': t1.x.d}})

if __name__ == '__main__':
    print('t1:')
    print(t1)

    print('t2:')
    print(t2)
