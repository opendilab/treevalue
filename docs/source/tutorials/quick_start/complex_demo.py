import importlib.util
import os
from functools import lru_cache

_FILE_NAME = 'create_a_complex_tree.demo.py'
_, _SIMPLE_FILE_NAME = os.path.split(_FILE_NAME)
_MODULE_NAME, _ = _SIMPLE_FILE_NAME.split('.', maxsplit=1)


@lru_cache()
def _get_module():
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _FILE_NAME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


_module = _get_module()
t1, t2, t3 = _module.t1, _module.t2, _module.t3
