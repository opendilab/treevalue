from .tree import TreeValue, _get_data_property


def to_json(tree: TreeValue):
    return _get_data_property(tree).to_json()
