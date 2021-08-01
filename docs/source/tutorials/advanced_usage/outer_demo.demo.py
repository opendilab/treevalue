from treevalue import FastTreeValue, func_treelize


# missing value is very important when use outer mode
@func_treelize(mode='outer', missing=0)
def plus(a, b):
    return a + b


if __name__ == '__main__':
    t1 = FastTreeValue({'b': 2, 'x': {'c': 3, 'd': 4, 'e': 5, 'f': 6}})
    t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 48, 'e': 54}})

    print('plus(t1, t2):', plus(t1, t2))
