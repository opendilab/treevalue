from functools import partial, wraps, reduce
from operator import __and__
from queue import Queue
from typing import TypeVar, Type, Union, Collection, Set

_ClassType = TypeVar('_ClassType')


def class_wraps(original_class: Type[_ClassType]):
    """
    Overview:
        Wrap class like functools.wraps, can be used in class decorators.

    Arguments:
        - original_class (:obj:`Type[_ClassType]`): Original class for wrapping.

    Example:
        >>> def cls_dec(clazz):
        >>>     @class_wraps(clazz)
        >>>     class _NewClazz(clazz):
        >>>         pass
        >>>
        >>>     return _NewClazz
    """

    # noinspection PyTypeChecker
    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        new_clazz = type(original_class.__name__, (clazz,), {
            '__doc__': original_class.__doc__,
            '__module__': original_class.__module__,
        })
        return new_clazz

    return _decorator


def init_magic(init_decorator):
    """
    Overview:
        Magic for initialization function of a class.

    Arguments:
        - init_decorator (:obj:`Callable`): Initialization function decorator.

    Example:
        >>> from functools import wraps
        >>>
        >>> def _init_dec(func):
        >>>     @wraps(func)
        >>>     def _new_func(value):
        >>>         func(value + 1)
        >>>
        >>>     return _new_func
        >>>
        >>> @init_magic(_init_dec)
        >>> class Container:
        >>>     def __init__(self, value):
        >>>         self.__value = value
        >>>
        >>>     @property
        >>>     def value(self):
        >>>         return self.__value
        >>>
        >>> c = Container(1)
        >>> c.value   # 2
        >>> c2 = Container(33)
        >>> c2.value  # 34
    """

    def _decorator(clazz: Type[_ClassType]) -> Type[_ClassType]:
        @class_wraps(clazz)
        class _NewClass(clazz):
            @wraps(clazz.__init__)
            def __init__(self, *args, **kwargs):
                init_decorator(partial(clazz.__init__, self))(*args, **kwargs)

        return _NewClass

    return _decorator


def _get_all_bases(clazz: Type):
    queue = Queue()
    result = {clazz}
    queue.put(clazz)
    while not queue.empty():
        current = queue.get()
        for _type in current.__bases__:
            if _type not in result:
                result.add(_type)
                queue.put(_type)

    return result


def _get_all_direct_bases(clazz: Type):
    result = set()
    while True:
        result.add(clazz)
        clazz = clazz.__base__
        if clazz is None:
            break

    return result


def _base_process(base: Union[Collection[Type], Type, None]):
    if isinstance(base, type):
        base = (base,)
    elif base is not None:
        base = tuple(list(base))

    return base


def _all_commons(*classes: Type, func, base: Union[Collection[Type], Type, None] = None) -> Set[Type]:
    if not classes:
        return set()

    base = _base_process(base)
    _intersection = reduce(__and__, [func(item) for item in classes])
    _result = set()

    for _base_class in _intersection:
        acceptable = True
        for _another_base_class in _intersection:
            if _base_class == _another_base_class:
                continue

            if issubclass(_another_base_class, _base_class):
                acceptable = False
                break

        if acceptable:
            _result.add(_base_class)

    if base:
        _result = {item for item in _result if issubclass(item, base)}

    return _result


def common_bases(*classes: Type, base: Union[Collection[Type], Type, None] = None) -> Set[Type]:
    """
    Overview:
        Get all the common bases of the classes.

    Arguments:
        - classes (:obj:`Type`): Target classes.
        - base (:obj:`Union[Collection[Type], Type, None]`): Limit of the base class, \
            default is `None` which means no limit.

    Returns:
        - bases (:obj:`Set[Type]`): A set of classes which is the common bases of the classes, \
            only high leveled classes will be kept.
    """
    return _all_commons(*classes, func=_get_all_bases, base=base)


def common_direct_base(*classes: Type, base: Union[Collection[Type], Type, None] = None):
    """
    Overview:
        Get the common direct base of the classes.

    Arguments:
        - classes (:obj:`Type`): Target classes.
        - base (:obj:`Union[Collection[Type], Type, None]`): Limit of the base class, \
            default is `None` which means no limit.

    Returns:
        - base (:obj:`Type`): A class which is all the bases.
    """
    base = _base_process(base)
    _bases = _all_commons(*classes, func=_get_all_direct_bases, base=base)
    if _bases:
        return list(_bases)[0]
    else:
        if base:
            template = "No common base found with {classes} which is based on {bases}."
        else:
            template = "No common base found with {classes}."

        raise TypeError(template.format(classes=repr(classes), bases=repr(base)))


def get_class_full_name(clazz: type):
    """
    Overview:
        Get full name of a class.

    Arguments:
        - clazz (:obj:`type`): Given class.

    Returns:
        - name (:obj:`str`): Full name of the given class.
    """
    module = clazz.__module__
    if not module or module == 'builtins':
        return clazz.__name__
    else:
        return module + '.' + clazz.__name__
