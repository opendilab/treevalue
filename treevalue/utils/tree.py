from queue import Queue

from treelib import Tree as LibTree

_ROOT_ID = '_root'
_NODE_ID_TEMP = '_node_{id}'


def build_tree(root, represent=None, iterate=None, recurse=None) -> LibTree:
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
