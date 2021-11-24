from treevalue import TreeValue, raw, flatten

if __name__ == '__main__':
    t = TreeValue({
        'a': 1,
        'b': 2,
        'c': raw({'x': 3, 'y': 4}),
        'd': {
            'x': 3,
            'y': 4
        },
    })

    print('flatten(t):')
    print(flatten(t))
