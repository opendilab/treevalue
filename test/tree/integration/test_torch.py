from typing import Tuple, Mapping
from unittest import skipUnless

import pytest
from hbutils.testing import vpip, OS, vpython

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

    @skipUnless(vpip('torch') >= '2.0.0' and OS.linux and vpython < '3.11', 'Torch 2 on linux platform required')
    def test_torch_compile(self):
        @torch.compile
        def foo(x, y, t):
            z = (x + y * 2000) / (t - 100)
            return z

        a = torch.randn(3, 4)
        b = torch.randn(3, 4)
        c = torch.randn(3, 4)
        assert torch.isclose(foo(a, b, c), (a + b * 2000) / (c - 100)).all()

    @skipUnless(vpip('torch') >= '2.0.0' and OS.linux and vpython < '3.11', 'Torch 2 on linux platform required')
    def test_torch_compile_buggy(self):
        @torch.compile
        def foox(x, y):
            z = x + y
            return z

        x = FastTreeValue({
            'a': torch.randn(3, 4) + 200,
            'b': torch.randn(5) - 300,
        })
        y = FastTreeValue({
            'a': torch.rand(4) + 500,
            'b': torch.randn(4, 5) + 1000,
        })

        _t_isclose = FastTreeValue.func()(torch.isclose)

        assert _t_isclose(foox(x, y), x + y).all() == \
               FastTreeValue({'a': torch.tensor(True), 'b': torch.tensor(True)})

    @skipUnless(vpip('torch') >= '2.0.0' and OS.linux and vpython < '3.11', 'Torch 2 on linux platform required')
    def test_with_module(self):
        from torch import nn

        class MLP(nn.Module):
            def __init__(self, in_features: int, out_features: int, layers: Tuple[int, ...] = (1024,)):
                nn.Module.__init__(self)
                self.in_features = in_features
                self.out_features = out_features
                self.layers = layers
                ios = [self.in_features, *self.layers, self.out_features]
                self.mlp = nn.Sequential(
                    *(
                        nn.Linear(in_, out_, bias=True)
                        for in_, out_ in zip(ios[:-1], ios[1:])
                    )
                )

            def forward(self, x):
                return self.mlp(x)

        class MultiHeadMLP(nn.Module):
            def __init__(self, in_features: int, out_features: Mapping[str, int], layers: Tuple[int, ...] = (1024,)):
                nn.Module.__init__(self)
                self.in_features = in_features
                self.out_features = out_features
                self.layers = layers
                _networks = {
                    o_name: MLP(in_features, o_feat, layers)
                    for o_name, o_feat in self.out_features.items()
                }
                self.mlps = nn.ModuleDict(_networks)
                self._t_mlps = FastTreeValue(_networks)

            def forward(self, x):
                return self._t_mlps(x)

        net = MultiHeadMLP(
            20,
            {'a': 10, 'b': 20, 'c': 14, 'd': 3},
        )
        net = torch.compile(net)

        input1 = torch.randn(3, 20)
        output1 = net(input1)
        assert output1.shape == FastTreeValue({
            'a': torch.Size([3, 10]),
            'b': torch.Size([3, 20]),
            'c': torch.Size([3, 14]),
            'd': torch.Size([3, 3]),
        })

        input2 = FastTreeValue.func()(torch.randn)(FastTreeValue({
            'a': (3, 20),
            'b': (4, 20),
            'c': (20,),
            'd': (2, 5, 20),
        }))
        output2 = net(input2)
        assert output2.shape == FastTreeValue({
            'a': torch.Size([3, 10]),
            'b': torch.Size([4, 20]),
            'c': torch.Size([14]),
            'd': torch.Size([2, 5, 3]),
        })

    @skipUnless(vpip('torch') and OS.linux and vpython < '3.11', 'torch required')
    def test_moduledict(self):
        with torch.no_grad():
            md = torch.nn.ModuleDict({
                'a': torch.nn.Linear(3, 5),
                'b': torch.nn.Linear(3, 6),
            })
            t = FastTreeValue(md)

            input_ = torch.randn(2, 3)
            output_ = t(input_)

            assert output_.shape == FastTreeValue({
                'a': (2, 5),
                'b': (2, 6),
            })
