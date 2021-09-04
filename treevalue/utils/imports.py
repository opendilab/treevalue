import builtins
import fnmatch
import importlib
from itertools import islice
from queue import Queue
from typing import Optional, Callable, Any, Tuple, Iterator

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


def quick_import_object(full_name: str, predicate: Optional[Callable] = None) -> Tuple[Any, str, str]:
    """
    Overview:
        Quickly dynamically import an object with a single name.

    Arguments:
        - full_name (:obj:`str`): Full name of the object, attribute is supported as well.
        - predicate (:obj:`Callable`): Predicate function, default is ``None`` means no limitation.

    Returns:
        - obj (:obj:`Tuple[Any, str, str]`): Imported object.

    Example::
        >>> quick_import_object('zip')                     # <class 'zip'>, '', 'zip'
        >>> quick_import_object('numpy.ndarray')           # <class 'numpy.ndarray'>, 'numpy', 'ndarray'
        >>> quick_import_object('numpy.ndarray.__name__')  # 'ndarray', 'numpy', 'ndarray.__name__'
    """
    _iter = islice(iter_import_objects(full_name, predicate), 1)

    try:
        # noinspection PyTupleAssignmentBalance
        _obj, _module, _name = next(_iter)
        return _obj, _module, _name
    except (StopIteration, StopAsyncIteration):
        raise ImportError(f'Cannot import object {repr(full_name)}.')


def iter_import_objects(full_pattern: str, predicate: Optional[Callable] = None) \
        -> Iterator[Tuple[Any, str, str]]:
    """
    Overview:
        Quickly dynamically import all objects with full name pattern.

    Arguments:
        - full_pattern (:obj:`str`): Full pattern of the object, attribute is supported as well.
        - predicate (:obj:`Callable`): Predicate function, default is ``None`` means no limitation.

    Returns:
        - iter (:obj:`Iterator[Tuple[Any, str, str]]`): Iterator for all the imported objects.
    """
    predicate = dynamic_call(predicate or (lambda: True))

    segments = full_pattern.split('.')
    length = len(segments)
    _errs = []
    for i in reversed(range(length + 1)):
        module_name = '.'.join(segments[:i])
        attrs = tuple(segments[i:])
        attrs_count = len(attrs)

        try:
            module = importlib.import_module(module_name or 'builtins')
        except (ModuleNotFoundError, ImportError):
            continue

        queue = Queue()
        queue.put((module, 0, ()))
        exist = False

        while not queue.empty():
            root, pos, ats = queue.get()

            if pos >= attrs_count:
                obj_name = '.'.join(ats)
                if predicate(root, module_name, obj_name):
                    yield root, module_name, obj_name
            elif hasattr(root, attrs[pos]):
                queue.put((getattr(root, attrs[pos]), pos + 1, ats + (attrs[pos],)))
                exist = True
            elif hasattr(root, '__dict__'):
                for key, value in sorted(root.__dict__.items()):
                    if fnmatch.fnmatch(key, attrs[pos]):
                        queue.put((value, pos + 1, ats + (key,)))
                        exist = True

        if exist:
            break
