from treevalue import FastTreeValue, mask

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'y': {'e': 6, 'f': 8}})
    m = FastTreeValue({'a': True, 'b': False, 'x': {'c': True, 'd': True}, 'y': {'e': False, 'f': False}})

    print('mask(t, m):')
    print(mask(t, m))

    print('mask(t, m, remove_empty=False):')
    print(mask(t, m, remove_empty=False))
