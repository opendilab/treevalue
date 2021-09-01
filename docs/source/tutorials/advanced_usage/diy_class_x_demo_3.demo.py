import os

from treevalue import general_tree_value


class DemoTreeValue(general_tree_value(methods=dict(
    # - operator will be disabled
    __sub__=NotImplemented,
    __rsub__=NotImplemented,
    __isub__=NotImplemented,

    # / operator will raise ArithmeticError
    __truediv__=ArithmeticError('True div is not supported'),
    __rtruediv__=ArithmeticError('True div is not supported'),
    __itruediv__=ArithmeticError('True div is not supported'),

    # +t will be changed to t * 2
    __pos__=lambda x: x * 2,
))):
    pass


if __name__ == '__main__':
    t1 = DemoTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = DemoTreeValue({'a': 11, 'b': 24, 'x': {'c': 30, 'd': 47}})

    # __add__ can be used normally
    print('t1 + t2:', t1 + t2, sep=os.linesep)

    # __sub__ will cause TypeError due to the NotImplemented
    try:
        _ = t1 - t2
    except TypeError as err:
        print('t1 - t2:', err, sep=os.linesep)
    else:
        assert False, 'Should not reach here!'

    # __truediv__ will cause ArithmeticError
    try:
        _ = t1 / t2
    except ArithmeticError as err:
        print('t1 / t2:', err, sep=os.linesep)
    else:
        assert False, 'Should not reach here!'

    # __pos__ will be like t1 * 2
    print('+t1:', +t1, sep=os.linesep)
