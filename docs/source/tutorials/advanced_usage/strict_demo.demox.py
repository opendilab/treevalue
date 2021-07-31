from treevalue import FastTreeValue, func_treelize


@func_treelize(mode='strict')
def plus(a, b):
    return a + b


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 5}})
    t2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 48, 'e': 54}})
    t4 = FastTreeValue({'b': 2, 'x': {'c': 3, 'd': 4, 'e': 5, 'f': 6}})

    print('t1 + t2:', t1 + t2)
    print('t4 + t2:', t4 + t2)
