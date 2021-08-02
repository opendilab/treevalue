from treevalue import TreeValue

if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue(t1)  # use the same memory with t1

    print("Initial t1:")
    print(t1)
    print("Initial t2:")
    print(t2)
    print()

    t1.a, t1.x.c = 7, 5  # only t1 is updated in code
    print("Updated t1:")
    print(t1)
    print("Updated t2:")
    print(t2)
    print()
