from treevalue import FastTreeValue

t1 = FastTreeValue({
    'a': 1,
    'b': [2] * 1000,  # huge array
    'x': {
        'c': b'aklsdfj' * 2000,  # huge bytes
        'd': 4
    }
})
