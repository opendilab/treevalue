import warnings
from functools import wraps

try:
    import jax
    from jax.tree_util import register_pytree_node
except (ModuleNotFoundError, ImportError):
    from .cjax import register_for_jax as _original_register_for_jax


    @wraps(_original_register_for_jax)
    def register_for_jax(cls):
        warnings.warn(f'Jax doesn\'t have tree_util module due to either not installed '
                      f'or the installed version is too low, '
                      f'so the registration of {cls!r} will be ignored.')
else:
    from .cjax import register_for_jax
    from ..tree import TreeValue
    from ..general import FastTreeValue

    register_for_jax(TreeValue)
    register_for_jax(FastTreeValue)
