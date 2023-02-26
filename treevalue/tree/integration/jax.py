import warnings
from functools import wraps

try:
    import jax
except (ModuleNotFoundError, ImportError):
    from .cjax import register_for_jax as _original_register_for_jax


    @wraps(_original_register_for_jax)
    def register_for_jax(cls):
        warnings.warn(f'Jax is not installed, registration of {cls!r} will be ignored.')
else:
    from .cjax import register_for_jax
    from ..tree import TreeValue
    from ..general import FastTreeValue

    register_for_jax(TreeValue)
    register_for_jax(FastTreeValue)
