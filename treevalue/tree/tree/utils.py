from typing import TypeVar, List

from .tree import TreeValue, get_data_property

_TreeValue = TypeVar("_TreeValue", bound=TreeValue)


def jsonify(tree: _TreeValue):
    return get_data_property(tree).json()


def view(tree: _TreeValue, path: List[str]) -> _TreeValue:
    return tree.__class__(get_data_property(tree).view(path))


def clone(tree: _TreeValue) -> _TreeValue:
    return tree.__class__(get_data_property(tree).json())
