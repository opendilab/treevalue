import builtins
import importlib
from typing import Optional, Callable, Mapping, Any

from .func import dynamic_call


def _import_module(module_name=None):
    if module_name:
        return importlib.import_module(module_name)
    else:
        return builtins


def import_object(obj_name: str, module_name: Optional[str] = None):
    """
    Overview:
        Dynamically import an object from module.

    Arguments:
        - obj_name (:obj:`str`): Name of the object.
        - module_name (:obj:`Optional[str]`): Name of the module, \
            default is ``None`` which means the ``builtins`` module.

    Returns:
        - obj: Imported object.

    Example::
        >>> import_object('zip')               # <class 'zip'>
        >>> import_object('ndarray', 'numpy')  # <class 'numpy.ndarray'>
    """
    return getattr(_import_module(module_name), obj_name)


def import_all(module_name: Optional[str] = None,
               predicate: Optional[Callable] = None) -> Mapping[str, Any]:
    """
    Overview:
        Import all the objects in module.

    Arguments:
        - module_name (:obj:`Optional[str]`): Name of the module, \
            default is ``None`` which means the ``builtins`` module.
        - predicate (:obj:`Optional[Callable]`): Object predicate function, \
            default is ``None`` which means all the items is accepted.

    Returns:
        - objects (:obj:`Mapping[str, Any]`): Imported objects and their names.

    Examples:
        >>> import_all()                                              # all the objects in ``builtins``
        >>> import_all(predicate=lambda k, v: k in {'zip', 'print'})  # {'print': <built-in function print>, 'zip': <class 'zip'>}
    """
    predicate = dynamic_call(predicate or (lambda: True))
    return {key: value for key, value
            in _import_module(module_name).__dict__.items() if predicate(key, value)}


def quick_import_object(full_name: str):
    """
    Overview:
        Quickly dynamically import an object with a single name.

    Arguments:
        - full_name (:obj:`str`): Full name of the object, attribute is supported as well.

    Returns:
        - obj: Imported object.

    Example::
        >>> quick_import_object('zip')                     # <class 'zip'>
        >>> quick_import_object('numpy.ndarray')           # <class 'numpy.ndarray'>
        >>> quick_import_object('numpy.ndarray.__name__')  # 'ndarray', attribute is also supported.
    """
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
