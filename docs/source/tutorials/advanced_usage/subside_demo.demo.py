from treevalue import TreeValue, subside

if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue({'a': -14, 'b': 9, 'x': {'c': 3, 'd': 8}})
    t3 = TreeValue({'a': 6, 'b': 0, 'x': {'c': -5, 'd': 17}})
    t4 = TreeValue({'a': 0, 'b': -17, 'x': {'c': -8, 'd': 15}})
    t5 = TreeValue({'a': 3, 'b': 9, 'x': {'c': 11, 'd': -17}})

    st = {'first': (t1, t2), 'second': [t3, {'x': t4, 'y': t5}]}
    print("subside(st):")
    print(subside(st))
