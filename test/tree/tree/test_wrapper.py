from collections import namedtuple
from functools import wraps
from itertools import chain
from unittest import skipUnless

import numpy as np
import pytest
from hbutils.testing import vpip

from treevalue import penetrate, PENETRATE_SESSIONID_ARGNAME, FastTreeValue, raw, TreeValue

nt = namedtuple('nt', ['v1', 'v2'])


class MyTreeValue(FastTreeValue):
    pass


def _my_decorator(func):
    @wraps(func)
    def _new_func(*args, **kwargs):
        for index, item in chain(enumerate(args), kwargs.items()):
            if not isinstance(item, (dict, list, np.ndarray, int, float)):
                raise ValueError(f'wtf??? - {index!r}, {item!r}')

        return func(*args, **kwargs)

    return _new_func


@penetrate(_my_decorator)
def custom(x, y):
    return MyTreeValue({
        'a': x.t + y.z,
        'b': raw({
            'x': x.p['a'] * y.p['b'],
            'k': nt(x.p['a'] + 1, y.p['b'] - 0.5),
        })
    })


@_my_decorator
def custom_native(x, y):
    return MyTreeValue({
        'a': x.t + y.z,
        'b': raw({
            'x': x.p['a'] * y.p['b'],
            'k': nt(x.p['a'] + 1, y.p['b'] - 0.5),
        })
    })


@pytest.mark.unittest
class TestTreeTreeWrapper:
    @skipUnless(vpip('jax'), 'jax required but not installed')
    def test_penetrate_with_jit(self):
        import jax
        @penetrate(jax.jit, static_argnames=PENETRATE_SESSIONID_ARGNAME)
        def mul(x, y):
            return (x + 1) * y

        @penetrate(jax.jit)
        def mul_native(x, y):
            return (x + 1) * y

        t1 = FastTreeValue({
            'a': np.random.randint(0, 10, (2, 3)),
            'b': {
                'x': np.asarray(233.0),
                'y': np.random.randn(2, 3)
            }
        })
        assert FastTreeValue.func()(np.isclose)(mul(t1, 2), (t1 + 1) * 2).all() == \
               FastTreeValue({'a': True, 'b': {'x': True, 'y': True}})

        t2 = FastTreeValue({
            'a': np.random.randint(0, 10, (2, 3)),
            'b': {
                'x': np.asarray(-23.1),
                'y': np.random.randn(2, 3)
            }
        })
        assert FastTreeValue.func()(np.isclose)(mul(t1, y=t2), (t1 + 1) * t2).all() == \
               FastTreeValue({'a': True, 'b': {'x': True, 'y': True}})

        with pytest.raises(RuntimeError):
            _ = mul_native(t1, 2)

    def test_penetrate_with_custom(self):
        a1 = np.random.randint(0, 10, (2, 3))
        a2 = np.random.randn(2, 3)
        a3 = np.random.randint(0, 10, (2, 3))
        a4 = np.random.randn(2, 3)

        t1 = FastTreeValue({'t': a1, 'p': raw({'a': a2})})
        t2 = FastTreeValue({'z': a3, 'p': raw({'b': a4})})

        with pytest.raises(ValueError):
            _ = custom_native(t1, t2)

        result = custom(t1, y=t2)
        assert isinstance(result, MyTreeValue)
        assert np.isclose(result.a, a1 + a3).all()
        assert isinstance(result.b, dict) and not isinstance(result.b, TreeValue)
        assert np.isclose(result.b['x'], a2 * a4).all()
        assert isinstance(result.b['k'], nt)
        assert np.isclose(result.b['k'].v1, a2 + 1).all()
        assert np.isclose(result.b['k'].v2, a4 - 0.5).all()
