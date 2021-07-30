from functools import wraps

import pytest

from treevalue.utils import args_iter, dynamic_call, static_call


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

    def __get_wrapped_function(self):
        def _wrapper(func):
            @wraps(func)
            def _new_func(*args):
                return func(sum(args))

            return _new_func

        @dynamic_call
        @dynamic_call
        @_wrapper
        def f(x):
            return x ** x

        return f

    def test_dynamic_call_nested_with_wrapper(self):
        f = self.__get_wrapped_function()
        assert f(1, 2, 3, 4) == 10 ** 10

    def test_static_call(self):
        f = self.__get_wrapped_function()
        f = static_call(f, static_ok=False).__wrapped__
        assert f(2) == 4
        with pytest.raises(TypeError):
            _ = f(1, 2, 3, 4)

        def another_f(x):
            return x ** x

        with pytest.raises(TypeError):
            _ = static_call(another_f, static_ok=False)
