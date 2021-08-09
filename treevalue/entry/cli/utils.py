import io
import sys
import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Union, Tuple

import click

from ...utils import dynamic_call


def _validator(func):
    func = dynamic_call(func)

    @wraps(func)
    def _new_func(ctx, param, value):
        return func(ctx=ctx, param=param, value=value)

    return _new_func


def _multiple_validator(func):
    func = _validator(func)

    @wraps(func)
    def _new_func(ctx, param, value):
        return [func(ctx, param, item) for item in value]

    return _new_func


_EXPECTED_TREE_ERRORS = (
    ValueError, TypeError, ImportError, AttributeError, ModuleNotFoundError,
    FileNotFoundError, IsADirectoryError, PermissionError, FileExistsError,
)

_EXCEPTION_WRAPPED = '__exception_wrapped__'


def _err_validator(types: Union[type, Tuple[type]]):
    def _decorator(func):
        func = _validator(func)

        @wraps(func)
        def _new_func(ctx, param, value):
            try:
                return func(ctx, param, value)
            except click.BadParameter as err:
                raise err
            except types as err:
                _messages = [item for item in err.args if isinstance(item, str)]
                _final_message = _messages[0] if _messages else str(_messages)
                raise click.BadParameter(_final_message)

        return _new_func

    return _decorator


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
        click.secho(_print_exception(err), file=sys.stderr)
        raise err
    else:
        click.secho(click.style(ok(), fg='green'), nl=False)
    finally:
        click.echo('.', nl=True)


def _print_exception(err: BaseException) -> str:
    with io.StringIO() as fs:
        traceback.print_exception(type(err), err, err.__backtrace__, file=fs)
        return fs.getvalue()
