from typing import Type

from .general import generic_flatten, generic_unflatten, register_integrate_container, generic_mapping
from .jax import register_for_jax
from .torch import register_for_torch
from ..tree import TreeValue


def register_treevalue_class(cls: Type[TreeValue], r_jax: bool = True, r_torch: bool = True):
    """
    Overview:
        Register treevalue class into all existing types.

    :param cls: TreeValue class.
    :param r_jax: Register for jax, default is `True`.
    :param r_torch: Register for torch, default is `True`.
    """
    if r_jax:
        register_for_jax(cls)
    if r_torch:
        register_for_torch(cls)
