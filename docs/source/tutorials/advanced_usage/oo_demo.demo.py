from treevalue import FastTreeValue

if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = FastTreeValue({'a': 5, 'b': 6, 'x': {'c': 7, 'd': 8}})

    # operator support
    print('t1 + t2:')
    print(t1 + t2)
    print('t2 ** t1:')
    print(t2 ** t1)
    print()

    # utilities support
    print('t1.map(lambda x: (x + 1) * (x + 2)):')
    print(t1.map(lambda x: (x + 1) * (x + 2)))
    print('t1.reduce(lambda **kwargs: sum(kwargs.values())):',
          t1.reduce(lambda **kwargs: sum(kwargs.values())))
    print()
    print()

    # linking usage
    print('t1.map(lambda x: (x + 1) * (x + 2)).filter(lambda x: x % 4 == 0):')
    print(t1.map(lambda x: (x + 1) * (x + 2)).filter(lambda x: x % 4 == 0))
    print()

    # structural support
    print("Union result:")
    print(FastTreeValue.union(
        t1.map(lambda x: (x + 1) * (x + 2)),
        t2.map(lambda x: (x - 2) ** (x - 1)),
    ).map(lambda x: 'first: %d, second: %d, which sum is %d' % (x[0], x[1], sum(x))))
    print()
