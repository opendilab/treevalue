from functools import wraps
from typing import Callable


def eq_extend(func: Callable[..., bool]):
    @wraps(func)
    def _new_func(a, b, *args, **kwargs):
        if isinstance(a, dict) and isinstance(b, dict):
            aks, bks = set(a.keys()), set(b.keys())
            if aks != bks:
                return False
            else:
                return all([_new_func(a[key], b[key], *args, **kwargs) for key in aks])
        elif (isinstance(a, tuple) and isinstance(b, tuple)) \
                or (isinstance(a, list) and isinstance(b, list)):
            length_a, length_b = len(a), len(b)
            if length_a != length_b:
                return False
            else:
                return all([_new_func(ai, bi, *args, **kwargs) for ai, bi in zip(a, b)])
        else:
            return func(a, b, *args, **kwargs)

    return _new_func


@eq_extend
def float_eq(a, b, eps=1e-5):
    return abs(a - b) < abs(eps)
