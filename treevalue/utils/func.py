from functools import wraps
from inspect import signature, Parameter
from itertools import chain
from typing import Callable


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

    return _new_func
