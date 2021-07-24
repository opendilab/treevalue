import pytest
import torch

from treevalue.tree import func_treelize, TreeValue, FastTreeValue, union


@pytest.mark.torchtest
def test():
    @func_treelize(inherit=True)
    def add(a, b):
        return a + b

    @func_treelize()
    def sin(a):
        return torch.sin(a)

    cos = func_treelize()(torch.cos)

    @func_treelize(inherit=True)
    def cat(a, b, dim):
        return torch.cat([a, b], dim=dim)

    @func_treelize(inherit=True)
    def stack(a, b, dim):
        return torch.stack([a, b], dim=dim)

    @func_treelize(inherit=True)
    def stack_all(items, dim):
        return torch.stack(items, dim=dim)

    @func_treelize(inherit=True)
    def split(a, split_size_or_sections, dim):
        return torch.split(a, split_size_or_sections, dim)

    @func_treelize(inherit=True)
    def mean(a, *args, **kwargs):
        return torch.mean(a, *args, **kwargs)

    @func_treelize(inherit=True)
    def clamp(a, *args, **kwargs):
        return torch.clamp(a, *args, **kwargs)

    @func_treelize(inherit=True)
    def to(a, *args, **kwargs):
        return a.to(*args, **kwargs)

    t1 = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(5)})
    t2 = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(5)})

    t3 = add(t1, t2)
    assert t3.a.shape == (4, 3)
    assert t3.b.shape == (5, )
    t4 = add(1, t2)
    assert t4.a.shape == (4, 3)
    assert t4.b.shape == (5, )
    assert t4.b.eq(t2.b + 1).all()

    t5 = sin(t1)
    assert t5.a.eq(torch.sin(t1.a)).all()
    assert t5.b.eq(torch.sin(t1.b)).all()
    t5 = cos(t1)
    assert t5.a.eq(torch.cos(t1.a)).all()
    assert t5.b.eq(torch.cos(t1.b)).all()

    t6 = t1[0]
    assert t6.a.shape == (3, )
    assert t6.b.shape == ()

    # t1a = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(6, 9), 'c': {'d': torch.randn(8, 2)}, 'e': [torch.randn(2, 3), torch.randn(2, 4)]})
    # t2a = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(6, 9), 'c': {'d': torch.randn(8, 2)}, 'e': [torch.randn(2, 3), torch.randn(2, 4)]})
    t1a = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(6, 9), 'c': {'d': torch.randn(8, 2)}})
    t2a = FastTreeValue({'a': torch.randn(4, 3), 'b': torch.randn(6, 9), 'c': {'d': torch.randn(8, 2)}})

    t6 = t1a[0]
    assert t6.a.shape == (3, )
    assert t6.b.shape == (9, )
    t6 = t1a[::2]
    assert t6.a.shape == (2, 3)
    assert t6.c.d.shape == (4, 2)
    t6 = t1a[slice(0, 3)]
    assert t6.a.shape == (3, 3)
    assert t6.a[1].eq(t1a.a[1]).all()
    # t6 = t1a[..., 1]
    # assert t6.a.shape == (4, )
    # t6 = t1a[..., 1:2]
    # assert t6.a.shape == (4, 1)

    t7 = cat(t1a, t2a, dim=0)
    assert t7.a.shape == (8, 3)
    assert t7.b.shape == (12, 9)
    t7 = cat(t1a, t2a, dim=1)
    assert t7.a.shape == (4, 6)
    assert t7.b.shape == (6, 18)

    t7 = stack(t1a, t2a, dim=0)
    assert t7.a.shape == (2, 4, 3)
    assert t7.b.shape == (2, 6, 9)
    t7 = stack(t1a, t2a, dim=1)
    assert t7.a.shape == (4, 2, 3)
    assert t7.b.shape == (6, 2, 9)

    t8 = split(t1a, 2, 0)
    # assert isinstance(t8.a, tuple)
    # assert t8.a[0].shape == (2, 3)
    # assert isinstance(t8, tuple)
    # assert t8[0].a.shape == (2, 3)

    t9 = mean(t1a)
    assert t9.a == t1a.a.mean()
    assert t9.b == t1a.b.mean()

    t10 = clamp(t1a, 0, 0.2)
    assert t10.a.eq(t1a.a.clamp(0, 0.2)).all()
    assert t10.c.d.eq(t1a.c.d.clamp(0, 0.2)).all()

    assert t1a.a.dtype == torch.float32
    t11 = to(t1a, torch.int64)
    assert t11.a.dtype == torch.int64

    def stack_spec(items, *args, **kwargs):
        return stack_all(FastTreeValue.subside(items), *args, **kwargs)

    t12 = stack_spec([t1a, t2a, t1a], dim=0)
    assert t12.a.shape == (3, 4, 3)
