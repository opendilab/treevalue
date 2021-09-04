from treevalue import FastTreeValue

t = FastTreeValue({
    'a': 1,
    'b': 2.3,
    'x': {
        'c': 'str',
        'd': [1, 2, None],
        'e': b'bytes',
    }
})

if __name__ == '__main__':
    print(t)
