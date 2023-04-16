from unittest import skipUnless

import pytest
from hbutils.testing import vpip, OS

from treevalue import FastTreeValue, register_for_torch

try:
    import torch
    from torch.utils._pytree import _register_pytree_node
except (ImportError, ModuleNotFoundError):
    torch = None


@pytest.mark.unittest
class TestTreeIntegrationTorch:
    @skipUnless(torch, 'Torch required.')
    def test_flatten_and_unflatten(self):
        arr1 = torch.randint(0, 10, (2, 3))
        arr2 = torch.randn(2, 3)
        t1 = FastTreeValue({'a': arr1, 'b': {'x': torch.asarray(233.0), 'y': arr2}})

        flatted, spec = torch.utils._pytree.tree_flatten(t1)
        assert isinstance(flatted, list)
        assert len(flatted) == 3
        assert torch.isclose(flatted[0], arr1).all()
        assert torch.isclose(flatted[1], torch.asarray(233.0)).all()
        assert torch.isclose(flatted[2], arr2).all()

        newt = torch.utils._pytree.tree_unflatten(flatted, spec)
        assert type(newt) == FastTreeValue
        assert FastTreeValue.func()(torch.isclose)(t1, newt).all()

        class MyTreeValue(FastTreeValue):
            pass

        register_for_torch(MyTreeValue)
        t2 = MyTreeValue({'a': arr1, 'b': {'x': torch.asarray(233.0), 'y': arr2}})
        flatted, spec = torch.utils._pytree.tree_flatten(t2)
        assert isinstance(flatted, list)
        assert len(flatted) == 3
        assert torch.isclose(flatted[0], arr1).all()
        assert torch.isclose(flatted[1], torch.asarray(233.0)).all()
        assert torch.isclose(flatted[2], arr2).all()

        newt2 = torch.utils._pytree.tree_unflatten(flatted, spec)
        assert type(newt2) == MyTreeValue
        assert MyTreeValue.func()(torch.isclose)(t2, newt2).all()

    @skipUnless(torch, 'Torch required.')
    def test_error_register(self):
        with pytest.raises(TypeError):
            register_for_torch(None)
        with pytest.raises(TypeError):
            register_for_torch(list)

    @skipUnless(not torch, 'No torch required')
    def test_ignored_register(self):
        class MyTreeValueX(FastTreeValue):
            pass

        with pytest.warns(UserWarning):
            register_for_torch(MyTreeValueX)

    @skipUnless(vpip('torch') >= '2.0.0' and not OS.windows, 'Torch 2 on non-windows platform required')
    def test_torch_compile(self):
        @torch.compile
        def foo(x, y, t):
            z = (x + y * 2000) / (t - 100)
            return z

        a = torch.randn(3, 4)
        b = torch.randn(3, 4)
        c = torch.randn(3, 4)
        assert torch.isclose(foo(a, b, c), (a + b * 2000) / (c - 100)).all()
