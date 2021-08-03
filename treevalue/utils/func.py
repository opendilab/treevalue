import warnings
from functools import wraps
from inspect import signature, Parameter
from itertools import chain
from typing import Callable, TypeVar

from .singleton import SingletonMark


def args_iter(*args, **kwargs):
    """
    Overview:
        Iterate all the arguments with index and value.
        If argument is in `args`, the index should be integer increasing from 0.
        If argument is in `kwargs`, the index should be string which meaning the argument's name.
        The numeric indices will appear before the string indices,
        and **the order of the string indices are not approved**.

    Arguments:
        - args (:obj:`Tuple[Any]`): Argument list
        - kwargs (:obj:`Dict[str, Any]`): Argument mapping

    Example:
        >>> for index, value in args_iter(1, 2, 3, a=1, b=2, c=3)):
        >>>     print(index, value)

        The output should be

        >>> 0 1
        >>> 1 2
        >>> 2 3
        >>> a 1
        >>> b 2
        >>> c 3
    """
    for _index, _item in chain(enumerate(args), sorted(kwargs.items())):
        yield _index, _item


_STATICAL = '__statical__'


def dynamic_call(func: Callable):
    """
    Overview:
        Decorate function to dynamic-call-supported function.

    Arguments:
        - func (:obj:`Callable`): Original function to be decorated.

    Returns:
        - new_func (:obj:`Callable`): Decorated function.

    Example:
        >>> dynamic_call(lambda x, y: x ** y)(2, 3)  # 8
        >>> dynamic_call(lambda x, y: x ** y)(2, 3, 4)  # 8, 3rd is ignored
        >>> dynamic_call(lambda x, y, t, *args: (args, (t, x, y)))(1, 2, 3, 4, 5)  # ((4, 5), (3, 1, 2))
        >>> dynamic_call(lambda x, y: (x, y))(y=2, x=1)  # (1, 2), key word supported
        >>> dynamic_call(lambda x, y, **kwargs: (kwargs, x, y))(1, k=2, y=3)  # ({'k': 2}, 1, 3)
    """
    if getattr(func, _STATICAL, None):
        return func

    enable_args, args_count = False, 0
    enable_kwargs, kwargs_set = False, set()

    for name, param in signature(func, follow_wrapped=False).parameters.items():
        if param.kind in {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD}:
            args_count += 1
        if param.kind in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            kwargs_set |= {name}
        if param.kind == Parameter.VAR_POSITIONAL:
            enable_args = True
        if param.kind == Parameter.VAR_KEYWORD:
            enable_kwargs = True

    def _get_args(*args):
        return args if enable_args else args[:args_count]

    def _get_kwargs(**kwargs):
        return kwargs if enable_kwargs else {key: value for key, value in kwargs.items() if key in kwargs_set}

    @wraps(func)
    def _new_func(*args, **kwargs):
        return func(*_get_args(*args), **_get_kwargs(**kwargs))

    setattr(_new_func, _STATICAL, True)
    return _new_func


def static_call(func: Callable, static_ok: bool = True):
    """
    Overview:
        Static call, anti-calculation of dynamic call.

    Arguments:
        - func (:obj:`Callable`): Given dynamic function.
        - static_ok (:obj:`bool`): Allow given function to be static, default is `True`.

    Returns:
        - static (:obj:`Callable`): Static function.
    """
    if not static_ok and not getattr(func, _STATICAL, None):
        raise TypeError("Given callable is already static.")

    return getattr(func, '__wrapped__', func)


def pre_process(processor: Callable):
    """
    Overview:
        Pre processor for function.

    Arguments:
        - processor (:obj:`Callable`): Pre processor.

    Returns:
        - decorator (:obj:`Callable`): Function decorator

    Example:
        >>> @pre_process(lambda x, y: (-x, (x + 2) * y))
        >>> def plus(a, b):
        >>>     return a + b
        >>>
        >>> plus(1, 2)  # 5, 5 = -1 + (1 + 2) * 2
    """
    _processor = dynamic_call(processor)

    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            pargs = _processor(*args, **kwargs)

            if isinstance(pargs, tuple) and len(pargs) == 2 \
                    and isinstance(pargs[0], (list, tuple)) \
                    and isinstance(pargs[1], (dict,)):
                args_, kwargs_ = tuple(pargs[0]), dict(pargs[1])
            elif isinstance(pargs, (tuple, list)):
                args_, kwargs_ = tuple(pargs), {}
            elif isinstance(pargs, (dict,)):
                args_, kwargs_ = (), dict(pargs)
            else:
                args_, kwargs_ = (pargs,), {}

            return func(*args_, **kwargs_)

        return _new_func

    return _decorator


def post_process(processor: Callable):
    """
    Overview:
        Post processor for function.

    Arguments:
        - processor (:obj:`Callable`): Post processor.

    Returns:
        - decorator (:obj:`Callable`): Function decorator

    Example:
        >>> @post_process(lambda x: -x)
        >>> def plus(a, b):
        >>>     return a + b
        >>>
        >>> plus(1, 2)  # -3
    """
    processor = dynamic_call(processor)

    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            _result = func(*args, **kwargs)
            return processor(_result)

        return _new_func

    return _decorator


NO_INITIAL = SingletonMark("no_initial")

_ElementType = TypeVar("_ElementType")


def freduce(init=NO_INITIAL, pass_kwargs: bool = True):
    """
    Overview:
        Make binary function be reducible.

    Arguments:
        - init (:obj:`Any`): Initial data generator or \
            initial data, default is `NO_INITIAL` which means no initial data. \
            Missing of positional arguments is forbidden.
        - pass_kwargs (:obj:`bool`): Pass kwargs into initial function and wrapped function or not, \
            default is `True` which means pass the arguments in.

    Returns:
        - decorator (:obj:`Callable`): Decorator for the original function.

    Example:
        >>> @freduce(init=0)
        >>> def plus(a, b):
        >>>     return a + b
        >>>
        >>> plus()            # 0
        >>> plus(1)           # 1
        >>> plus(1, 2)        # 3
        >>> plus(1, 2, 3, 4)  # 10
    """
    if init is NO_INITIAL:
        init_func = None
    else:
        init_func = dynamic_call(init if hasattr(init, '__call__') else (lambda: init))

    def _decorator(func):
        func = dynamic_call(func)

        @wraps(func)
        def _new_func(*args, **kwargs) -> _ElementType:
            if not pass_kwargs and kwargs:
                warnings.warn(SyntaxWarning(
                    "Key-word arguments detected but will not be passed due to the pass_kwargs setting - {kwargs}.".format(
                        kwargs=repr(kwargs))))
            kwargs = kwargs if pass_kwargs else {}

            if init_func is None:
                if not args:
                    raise SyntaxError(
                        "No less than 1 argument expected in function {func} but 0 found.".format(func=repr(func)))
                current = args[0]
                args = args[1:]
            else:
                current = init_func(**kwargs)

            for arg in args:
                current = func(current, arg, **kwargs)

            return current

        return _new_func

    return _decorator
