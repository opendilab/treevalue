from functools import wraps

from .modes import TreeCalcMode


def treeilize(mode, allow_missing: bool = False, missing_default=None, allow_inherit: bool = False):
    mode = TreeCalcMode.loads(mode)

    def _decorator(func):
        @wraps(func)
        def _new_func(*args, **kwargs):
            pass
            # return run_func(func, *args, **kwargs)

        return _new_func

    return _decorator
