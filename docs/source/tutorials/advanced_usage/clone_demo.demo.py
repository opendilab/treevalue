from treevalue import TreeValue, clone

if __name__ == '__main__':
    t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'y': {'e': 5, 'f': 6}}})

    print("Tree t:")
    print(t)

    print("clone(t):")
    print(clone(t))
