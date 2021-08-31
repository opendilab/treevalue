import os

from treevalue import TreeValue, method_treelize


class MyTreeValue(TreeValue):
    # return type will be automatically detected as `MyTreeValue`
    @method_treelize(self_copy=True)
    def append(self, b):
        return self + b


if __name__ == '__main__':
    t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue({'a': -14, 'b': 9, 'x': {'c': 3, 'd': 8}})
    t3 = TreeValue({'a': 6, 'b': 0, 'x': {'c': -5, 'd': 17}})

    print('t1:', t1, sep=os.linesep)
    _t1_id = id(t1)

    print('t1.append(t2).append(t3):',
          t1.append(t2).append(t3), sep=os.linesep)
    assert id(t1) == _t1_id
