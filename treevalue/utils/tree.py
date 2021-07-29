from queue import Queue

from treelib import Tree as LibTree

_ROOT_ID = '_root'
_NODE_ID_TEMP = '_node_{id}'


def build_tree(root, represent=None, iterate=None, recurse=None) -> LibTree:
    """
    Overview:
        Build a treelib object by an object.

    Arguments:
        - root (:obj:`Any`): Root object.
        - represent (:obj:`Optional[Callable]`): Represent function, default is primitive `repr`.
        - iterate (:obj:`Optional[Callable]`): Iterate function, default is `lambda x: x.items()`.
        - recurse (:obj:`Optional[Callable]`): Recurse check function, default is `lambda x: hasattr(x, 'items')`.

    Returns:
        - tree (:obj:`treelib.Tree`): Built tree.

    Example:
         >>> t = build_tree(
         >>>     {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'z': [1, 2], 'v': {'1': '2'}},
         >>>     represent=lambda x: '<node>' if isinstance(x, dict) else repr(x),
         >>>     recurse=lambda x: isinstance(x, dict),
         >>> )
         >>> print(t)

         The output should be

         >>> <node>
         >>> ├── 'a' --> 1
         >>> ├── 'b' --> 2
         >>> ├── 'v' --> <node>
         >>> │   └── '1' --> '2'
         >>> ├── 'x' --> <node>
         >>> │   ├── 'c' --> 3
         >>> │   └── 'd' --> 4
         >>> └── 'z' --> [1, 2]
    """
    represent = represent or repr
    iterate = iterate or (lambda x: x.items())
    recurse = recurse or (lambda x: hasattr(x, 'items'))

    _tree = LibTree()
    _tree.create_node(represent(root), _ROOT_ID)
    _index, _queue = 0, Queue()
    _queue.put((_ROOT_ID, root))

    while not _queue.empty():
        _parent_id, _parent_tree = _queue.get()

        for key, value in iterate(_parent_tree):
            _index += 1
            _current_id = _NODE_ID_TEMP.format(id=_index)
            _tree.create_node(
                "{key} --> {value}".format(key=repr(key), value=represent(value)),
                _current_id,
                _parent_id
            )
            if recurse(value):
                _queue.put((_current_id, value))

    return _tree
