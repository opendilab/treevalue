from potc import transvars

from treevalue import FastTreeValue, raw

r = raw({'a': 1, 'b': 2, 'c': [3, 4]})
t = FastTreeValue({
    'a': 1, 'b': 'this is a string',
    'c': [], 'd': {
        'x': raw({'a': 1, 'b': (None, Ellipsis)}),
        'y': {3, 4, 5}
    }
})
st = t._detach()
if __name__ == '__main__':
    _code = transvars(
        {'t': t, 'st': t._detach(), 'r': r},
        reformat='pep8'
    )
    print(_code)
