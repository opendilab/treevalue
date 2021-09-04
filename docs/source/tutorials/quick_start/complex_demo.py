import os

from dm import get_module

from treevalue import TreeValue

_module = get_module(os.path.abspath('create_a_complex_tree.demo.py'))
for key, value in _module.__dict__.items():
    if isinstance(value, TreeValue):
        locals()[key] = value
