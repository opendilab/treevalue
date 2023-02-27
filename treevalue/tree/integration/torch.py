import warnings
from functools import wraps

try:
    import torch
except (ModuleNotFoundError, ImportError):
    from .ctorch import register_for_torch as _original_register_for_torch


    @wraps(_original_register_for_torch)
    def register_for_torch(cls):
        warnings.warn(f'Torch is not installed, registration of {cls!r} will be ignored.')
else:
    from .ctorch import register_for_torch
    from ..tree import TreeValue
    from ..general import FastTreeValue

    register_for_torch(TreeValue)
    register_for_torch(FastTreeValue)
