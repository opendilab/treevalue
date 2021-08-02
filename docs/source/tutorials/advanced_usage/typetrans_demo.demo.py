from treevalue import TreeValue, method_treelize, FastTreeValue, typetrans


class MyTreeValue(TreeValue):
    @method_treelize()
    def pw(self):
        return (self + 1) * (self + 2)


if __name__ == '__main__':
    t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    print('t1:')
    print(t1)
    print('t1 ** 2:')
    print(t1 ** 2)
    print()

    # Transform t1 to MyTreeValue,
    # __pow__ operator will be disabled and pw method will be enabled.
    t2 = typetrans(t1, MyTreeValue)
    print('t2:')
    print(t2)
    print('t2.pw():')
    print(t2.pw())
    print()
