import importlib.util
import os
from types import ModuleType


def get_module(filename) -> ModuleType:
    _, _simple_filename = os.path.split(filename)
    _module_name, _ = _simple_filename.split('.', maxsplit=1)

    spec = importlib.util.spec_from_file_location(_module_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
