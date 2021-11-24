from treevalue import unflatten

if __name__ == '__main__':
    flatted = [
        (('a',), 1),
        (('b',), 2),
        (('c',), {'x': 3, 'y': 4}),
        (('d', 'x'), 3),
        (('d', 'y'), 4)
    ]

    print('unflatten(flatted):')
    print(unflatten(flatted))
