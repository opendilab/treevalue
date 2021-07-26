from treevalue import FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 4, 'd': 4}})
    print(t)
