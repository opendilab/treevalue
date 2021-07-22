import pytest

from treevalue.utils import args_iter, dynamic_call


@pytest.mark.unittest
class TestUtilsFunc:
    def test_args_iter(self):
        assert list(args_iter(1, 2, 3, a=1, c=3, b=4)) == [(0, 1), (1, 2), (2, 3), ('a', 1), ('b', 4), ('c', 3)]

    def test_dynamic_call(self):
        assert dynamic_call(lambda x, y: x ** y)(2, 3) == 8
        assert dynamic_call(lambda x, y: x ** y)(2, 3, 4) == 8
        assert dynamic_call(lambda x, y, t, *args: (args, (t, x, y)))(1, 2, 3, 4, 5) == ((4, 5), (3, 1, 2))
        assert dynamic_call(lambda x, y: (x, y))(y=2, x=1) == (1, 2)
        assert dynamic_call(lambda x, y, **kwargs: (kwargs, x, y))(1, k=2, y=3) == ({'k': 2}, 1, 3)
        assert dynamic_call(lambda x, y, *args, t=2, v=4, **kwargs: (args, kwargs, x, y, t, v))(1, 2, 3, 4, p=5, v=7) \
               == ((3, 4), {'p': 5}, 1, 2, 2, 7)
