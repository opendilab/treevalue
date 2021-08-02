# native plus between dictionaries
def plus(a, b):
    _result = {}
    for key in set(a.keys()) | set(b.keys()):
        if isinstance(a[key], int) and isinstance(b[key], int):
            _result[key] = a[key] + b[key]
        else:
            _result[key] = plus(a[key], b[key])

    return _result


if __name__ == "__main__":
    d1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    d2 = {'a': 11, 'b': 22, 'x': {'c': 30, 'd': 47}}

    print('plus(d1, d2):')
    print(plus(d1, d2))
