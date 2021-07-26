import os

from treevalue import FastTreeValue, func_treelize


@func_treelize()
def gcd(a, b):
    while True:
        r = a % b
        a, b = b, r
        if r == 0:
            break

    return a


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 2, 'b': 30, 'x': {'c': 4, 'd': 9}})
    t2 = FastTreeValue({'a': 4, 'b': 48, 'x': {'c': 6, 'd': 54}})

    print("Result of gcd(t1, t2):", gcd(t1, t2), sep=os.linesep)
    print("Result of gcd(12, 9):", gcd(12, 9))
