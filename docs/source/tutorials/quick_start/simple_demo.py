import os

from dm import get_module

_module = get_module(os.path.abspath('create_a_tree.demo.py'))
t = _module.t
