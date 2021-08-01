from treevalue import FastTreeValue, mapping, mask

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'y': {'e': 6, 'f': 8}})

    print('mask(t, mapping(t, lambda x: x % 2 == 1)):')
    print(mask(t, mapping(t, lambda x: x % 2 == 1)))

    print('mask(t, mapping(t, lambda x: x % 2 == 1), remove_empty=False):')
    print(mask(t, mapping(t, lambda x: x % 2 == 1), remove_empty=False))
