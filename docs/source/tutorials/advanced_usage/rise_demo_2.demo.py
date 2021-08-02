from treevalue import TreeValue, subside, rise

if __name__ == '__main__':
    # The same demo as the subside docs
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    t2 = TreeValue({'a': -14, 'b': 9, 'x': {'c': 3, 'd': 8}})
    t3 = TreeValue({'a': 6, 'b': 0, 'x': {'c': -5, 'd': 17}})
    t4 = TreeValue({'a': 0, 'b': -17, 'x': {'c': -8, 'd': 15}})
    t5 = TreeValue({'a': 3, 'b': 9, 'x': {'c': 11, 'd': -17}})
    st = {'first': (t1, t2), 'second': [t3, {'x': t4, 'y': t5}]}
    tx = subside(st)

    # Rising process, with template
    # only the top-leveled dict will be extracted,
    # neither tuple, list nor low-leveled dict will not be extracted
    # because they are not defined in `template` argument
    st2 = rise(tx, template={'first': None, 'second': [None, None]})
    print('st2:', st2)

    print("st2['first']:")
    print(st2['first'])

    print("st2['second'][0]:")
    print(st2['second'][0])

    print("st2['second'][1]:")
    print(st2['second'][1])
