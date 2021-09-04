import io
import traceback


def str_traceback(err: BaseException) -> str:
    """
    Overview:
        Get full backtrace for exception object.

    Arguments:
        - err (:obj:`BaseException`): Exception object.

    Returns:
        - backtrace (:obj:`str`): Full string backtrace.

    Example:
        >>> try:
        >>>     raise RuntimeError('runtime error')
        >>> except Exception as err:
        >>>     s = str_traceback(err)

        The output should be like

        >>> Traceback (most recent call last):
        >>>   File "<stdin>", line 2, in <module>
        >>>     raise RuntimeError('runtime error')
        >>> RuntimeError: runtime error
    """
    with io.StringIO() as fs:
        traceback.print_exception(type(err), err, err.__traceback__, file=fs)
        return fs.getvalue()
