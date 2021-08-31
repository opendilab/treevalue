import os

from dm import get_module

_module = get_module(os.path.abspath('create_a_complex_tree.demo.py'))
t1, t2, t3 = _module.t1, _module.t2, _module.t3
