from treevalue import mapping, FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

    print('mapping(t, lambda x: x ** x + 2):')
    print(mapping(t, lambda x: x ** x + 2))
