from treevalue import TreeValue

if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    storage = t1._detach()  # tree is the data tree
    data = storage.detach()

    print('t1:')
    print(t1)

    print('tree storage:')
    print(storage)

    print('data:')
    print(data)
