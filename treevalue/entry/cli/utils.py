from contextlib import contextmanager
from functools import wraps
from typing import Callable, Union

import click

from ...utils import dynamic_call


def _wrap_validator(func):
    func = dynamic_call(func)

    @wraps(func)
    def _new_func(ctx, param, value):
        return func(ctx=ctx, param=param, value=value)

    return _new_func


def _multiple_validator(func):
    func = _wrap_validator(func)

    @_exception_validation
    @wraps(func)
    def _new_func(ctx, param, value):
        return [func(ctx, param, item) for item in value]

    return _new_func


_EXPECTED_TREE_ERRORS = (
    ValueError, TypeError, ImportError, AttributeError, ModuleNotFoundError,
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


@contextmanager
def _click_pending(text: str, ok: Union[Callable, str] = 'OK', error: Union[Callable, str] = 'ERROR'):
    if not hasattr(ok, '__call__'):
        _okay_text = str(ok)
        ok = lambda: _okay_text
    ok = dynamic_call(ok)

    if not hasattr(error, '__call__'):
        _error_text = str(error)
        error = lambda: _error_text
    error = dynamic_call(error)

    click.echo(text, nl=False)

    try:
        yield
    except BaseException as err:
        click.secho(click.style(error(err), fg='red'), nl=False)
        raise err
    else:
        click.secho(click.style(ok(), fg='green'), nl=False)
    finally:
        click.echo('.', nl=True)
