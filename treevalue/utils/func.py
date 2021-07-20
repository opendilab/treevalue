from itertools import chain


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
