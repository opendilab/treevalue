import builtins
import importlib
from typing import Optional, Callable

from .func import dynamic_call


def _import_module(module_name=None):
    if module_name:
        return importlib.import_module(module_name)
    else:
        return builtins


def import_object(obj_name: str, module_name: Optional[str] = None):
    return getattr(_import_module(module_name), obj_name)


def import_all(module_name: Optional[str] = None, predicate: Optional[Callable] = None):
    predicate = dynamic_call(predicate or (lambda: True))
    return {key: value for key, value
            in _import_module(module_name).__dict__.items() if predicate(key, value)}


def quick_import_object(full_name: str):
    segments = full_name.split('.')
    length = len(segments)
    _errs = []
    for i in reversed(range(length)):
        import_path = '.'.join(segments[:i])
        root_obj_name = segments[i]
        sub_attrs = segments[i + 1:]

        try:
            obj = import_object(root_obj_name, import_path)
            for _attr in sub_attrs:
                obj = getattr(obj, _attr)
        except (AttributeError, ModuleNotFoundError, ImportError) as err:
            _errs.append(err)
        else:
            return obj

    raise _errs[0]
