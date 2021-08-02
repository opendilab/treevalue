from treevalue import TreeValue, view

if __name__ == '__main__':
    t = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'y': {'e': 5, 'f': 6}}})

    print("Tree t:")
    print(t)

    t_x_y = t.x.y
    vt_x_y = view(t, ['x', 'y'])

    print("t.x.y:")
    print(t_x_y)
    print("View of t, ['x', 'y']:")
    print(vt_x_y)

    t.x = TreeValue({'cc': 33, 'dd': 44, 'y': {'ee': 55, 'ff': 66}})

    print("t_x_y after replacement:")
    print(t_x_y)
    print("View of t, ['x', 'y'] after replacement:")
    print(vt_x_y)
