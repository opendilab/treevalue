from treevalue import TreeValue

if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    tree = t1._detach()  # tree is the data tree

    print('t1:')
    print(t1)

    print('tree:')
    print(tree)
