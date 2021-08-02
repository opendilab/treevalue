from treevalue import TreeValue, func_treelize


@func_treelize()
def plus(a, b):
    return a + b


if __name__ == "__main__":
    d1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    d2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 47}})

    print("plus(d1, d2):")
    print(plus(d1, d2))
