from treevalue import FastTreeValue, func_treelize


@func_treelize(mode='strict')
def plus(a, b):
    return a + b


@func_treelize(mode='strict', inherit=False)
def plusx(a, b):
    return a + b


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': 9})
    t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 48, 'e': 54}})

    print('plus(t1, t2):', plus(t1, t2))
    print('plus(t2, 5):', plus(t2, 5))
    print()

    print('plusx(t1, t2):', plusx(t1, t2))
    print()
