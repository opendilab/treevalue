from treevalue import TreeValue

t1 = TreeValue({
    'a': 2, 'b': 3,
    'x': {
        'c': 5, 'd': 7,
    }
})
t2 = TreeValue({
    't1': t1, 'a': 4, 'x': {'c': 5, 'd': t1.x}
})

if __name__ == '__main__':
    print(t2)
