import os

from treevalue import general_tree_value


class MyTreeValue(general_tree_value()):
    pass


if __name__ == '__main__':
    t1 = MyTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = MyTreeValue({'a': 11, 'b': 24, 'x': {'c': 30, 'd': 47}})

    # __add__ operator can be directly used
    print('t1 + t2:', t1 + t2, sep=os.linesep)
