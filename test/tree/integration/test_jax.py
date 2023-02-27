from unittest import skipUnless

import numpy as np
import pytest

from treevalue import FastTreeValue, register_for_jax

try:
    import jax
except (ModuleNotFoundError, ImportError):
    jax = None


@pytest.mark.unittest
class TestTreeTreeIntegration:
    @skipUnless(jax, 'Jax required.')
    def test_jax_double(self):
        @jax.jit
        def double(x):
            return x * 2 + 1.5

        t1 = FastTreeValue({
            'a': np.random.randint(0, 10, (2, 3)),
            'b': {
                'x': np.asarray(233.0),
                'y': np.random.randn(2, 3)
            }
        })
        r1 = double(t1)
        assert type(r1) is FastTreeValue
        assert FastTreeValue.func()(np.isclose)(r1, t1 * 2 + 1.5).all() == \
               FastTreeValue({'a': True, 'b': {'x': True, 'y': True}})

        class MyTreeValue(FastTreeValue):
            pass

        register_for_jax(MyTreeValue)

        t2 = MyTreeValue({
            'a': np.random.randint(0, 10, (2, 3)),
            'b': {
                'x': np.asarray(233.0),
                'y': np.random.randn(2, 3)
            }
        })
        r2 = double(t2)
        assert type(r2) is MyTreeValue
        assert MyTreeValue.func()(np.isclose)(r2, t2 * 2 + 1.5).all() == \
               MyTreeValue({'a': True, 'b': {'x': True, 'y': True}})

    @skipUnless(jax, 'Jax required.')
    def test_error_register(self):
        with pytest.raises(TypeError):
            register_for_jax(None)
        with pytest.raises(TypeError):
            register_for_jax(list)

    @skipUnless(not jax, 'No jax required')
    def test_ignored_register(self):
        class MyTreeValueX(FastTreeValue):
            pass

        with pytest.warns(UserWarning):
            register_for_jax(MyTreeValueX)
