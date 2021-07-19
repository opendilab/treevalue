from .tree import TreeValue, get_data_property


def to_json(tree: TreeValue):
    return get_data_property(tree).to_json()
