from treevalue import TreeValue, raw, walk

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

    for path, node in walk(t):
        print(path, '-->', node)
