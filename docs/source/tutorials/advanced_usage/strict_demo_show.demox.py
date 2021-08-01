import numpy as np

from treevalue import FastTreeValue, func_treelize


@func_treelize(mode='strict')
def plus(a, b):
    print("Current a and b:", type(a), a, type(b), b)
    return a + b


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 48, 'e': 54}})
    t2 = FastTreeValue({
        'a': np.array([1, 3, 5, 7]),
        'b': np.array([2, 5, 8, 11]),
        'x': {
            'c': 3,
            'd': 4.8,
            'e': np.array([[2, 3], [5, 6]]),
        }
    })
    t3 = FastTreeValue({
        'a': np.array([1, 3, 5, 7]),
        'b': [2, 5, 8, 11],
        'x': {
            'c': 3,
            'd': 4.8,
            'e': np.array([[2, 3], [5, 6]]),
        }
    })

    print('plus(t1, t2):', plus(t1, t2))
    print()
    print('plus(t1, t3):', plus(t1, t3))
    print()
