from unittest import skipUnless

import pytest

from treevalue import register_treevalue_class, FastTreeValue

try:
    import torch
except (ImportError, ModuleNotFoundError):
    torch = None

try:
    import jax
except (ModuleNotFoundError, ImportError):
    jax = None


@pytest.mark.unittest
class TestTreeIntegrationInit:
    @skipUnless(torch and jax, 'Torch and jax required.')
    def test_register_custom_class_all(self):
        class MyTreeValue(FastTreeValue):
            pass

        with pytest.warns(None):
            register_treevalue_class(MyTreeValue)

    @skipUnless(not torch or not jax, 'Not all torch and jax required.')
    def test_register_custom_class_some(self):
        class MyTreeValue(FastTreeValue):
            pass

        with pytest.warns(UserWarning):
            register_treevalue_class(MyTreeValue)
