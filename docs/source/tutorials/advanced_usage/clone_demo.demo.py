from treevalue import TreeValue, clone, raw

if __name__ == '__main__':
    t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'y': raw({'e': 5, 'f': 6})}})

    print("Tree t:")
    print(t)
    print("Id of t.x.y: %x" % id(t.x.y))
    print()
    print()

    print("clone(t):")
    print(clone(t))
    print("Id of clone(t).x.y: %x" % id(clone(t).x.y))
    print()
    print()

    print('clone(t, copy_value=True):')
    print(clone(t, copy_value=True))
    print("Id of clone(t, copy_value=True).x.y: %x" % id(clone(t, copy_value=True)))
    print()
    print()
