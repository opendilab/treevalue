import os

from treevalue import classmethod_treelize, TreeValue, method_treelize


class MyTreeValue(TreeValue):
    # return type will be automatically detected as `MyTreeValue`
    @method_treelize()
    def append(self, b):
        print("Append arguments:", self, b)
        return self + b

    # return type will be automatically detected as `MyTreeValue`
    @classmethod
    @classmethod_treelize()
    def sum(cls, *args):
        print("Sum arguments:", cls, *args)
        return sum(args)


if __name__ == '__main__':
    t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue({'a': -14, 'b': 9, 'x': {'c': 3, 'd': 8}})
    t3 = TreeValue({'a': 6, 'b': 0, 'x': {'c': -5, 'd': 17}})

    print('t1.append(t2).append(t3):',
          t1.append(t2).append(t3), sep=os.linesep)

    print('MyTreeValue.sum(t1, t2, t3):',
          MyTreeValue.sum(t1, t2, t3), sep=os.linesep)
