from unittest import skipUnless

import numpy as np
import pytest

from treevalue import FastTreeValue

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
        assert FastTreeValue.func()(np.isclose)(double(t1), t1 * 2 + 1.5).all() == \
               FastTreeValue({'a': True, 'b': {'x': True, 'y': True}})
