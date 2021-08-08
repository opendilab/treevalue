from functools import wraps

import click

from ...utils import dynamic_call


def _multiple_validator(func):
    func = dynamic_call(func)

    @_exception_validation
    @wraps(func)
    def _new_func(ctx, param, value):
        return [func(ctx=ctx, param=param, value=item) for item in value]

    return _new_func


_EXPECTED_TREE_ERRORS = (
    ValueError, TypeError, ImportError, AttributeError,
    FileNotFoundError, IsADirectoryError, PermissionError, FileExistsError,
)

_EXCEPTION_WRAPPED = '__exception_wrapped__'


def _exception_validation(func):
    if getattr(func, _EXCEPTION_WRAPPED, False):
        return func

    @wraps(func)
    def _new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except click.BadParameter as err:
            raise err
        except _EXPECTED_TREE_ERRORS as err:
            _first_message = [item for item in err.args if isinstance(item, str)][0]
            raise click.BadParameter(_first_message)

    setattr(_new_func, _EXCEPTION_WRAPPED, True)
    return _new_func


def _build_cli(base_cli, *wrappers):
    _cli = None
    for wrapper in wrappers:
        _cli = wrapper(_cli or base_cli)
    return _cli
