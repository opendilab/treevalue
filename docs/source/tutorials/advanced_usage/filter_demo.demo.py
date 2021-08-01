from treevalue import FastTreeValue, filter_

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'y': {'e': 6, 'f': 8}})

    print('filter_(t, lambda x: x % 2 == 1):')
    print(filter_(t, lambda x: x % 2 == 1))

    print('filter_(t, lambda x: x % 2 == 1, remove_empty=False):')
    print(filter_(t, lambda x: x % 2 == 1, remove_empty=False))
