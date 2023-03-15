import warnings
from functools import wraps

try:
    import torch
    from torch.utils._pytree import _register_pytree_node
except (ModuleNotFoundError, ImportError):
    from .ctorch import register_for_torch as _original_register_for_torch


    @wraps(_original_register_for_torch)
    def register_for_torch(cls):
        warnings.warn(f'Pytree module is not included in the Torch installation '
                      f'or the installed version is too low, '
                      f'so the registration of {cls!r} will be ignored.')
else:
    from .ctorch import register_for_torch
    from ..tree import TreeValue
    from ..general import FastTreeValue

    register_for_torch(TreeValue)
    register_for_torch(FastTreeValue)
