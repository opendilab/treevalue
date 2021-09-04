from treevalue import FastTreeValue

t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

if __name__ == '__main__':
    print(t)
