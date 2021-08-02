from treevalue import FastTreeValue, union

if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 5}})
    t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 48, 'e': 54}})
    t3 = FastTreeValue({'a': -13, 'b': -7, 'x': {'c': -5, 'd': -3, 'e': -2}})
    t4 = FastTreeValue({'a': -13, 'b': -7, 'x': 8})

    print("union(t1, t2):")
    print(union(t1, t2))

    print("union(t1, t2, t3):")
    print(union(t1, t2, t3))

    print("union(t1, t2, t3, t4):")
    print(union(t1, t2, t3, t4))
