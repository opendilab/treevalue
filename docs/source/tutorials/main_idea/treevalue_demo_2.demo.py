from treevalue import FastTreeValue

if __name__ == "__main__":
    d1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    d2 = FastTreeValue({'a': 11, 'b': 22, 'x': {'c': 30, 'd': 47}})

    print("d1 + d2:")
    print(d1 + d2)
