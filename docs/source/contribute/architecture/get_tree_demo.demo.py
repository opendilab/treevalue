from treevalue import TreeValue
from treevalue.tree.tree.tree import get_data_property

if __name__ == '__main__':
    t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
    tree = get_data_property(t1)  # tree is the data tree

    print('t1:')
    print(t1)

    print('tree:')
    print(tree)
