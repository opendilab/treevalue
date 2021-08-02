from functools import reduce
from operator import __mul__

from treevalue import utils_class, classmethod_treelize, TreeValue


class MyTreeValue(TreeValue):
    pass


# this is the utils class
@utils_class(return_type=MyTreeValue)
class CalcUtils:
    @classmethod
    @classmethod_treelize()
    def sum(cls, *args):
        print("Sum arguments:", cls, *args)
        return sum(args)

    @classmethod
    @classmethod_treelize()
    def mul(cls, *args):
        print("Mul arguments:", cls, *args)
        return reduce(__mul__, args, 1)


if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue({'a': -14, 'b': 9, 'x': {'c': 3, 'd': 8}})
    t3 = TreeValue({'a': 6, 'b': 0, 'x': {'c': -5, 'd': 17}})

    print('CalcUtils.sum(t1, t2, t3):')
    print(CalcUtils.sum(t1, t2, t3))

    print('CalcUtils.mul(t1, t2, t3):')
    print(CalcUtils.mul(t1, t2, t3))
