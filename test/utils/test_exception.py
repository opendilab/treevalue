import pytest

from treevalue.utils import str_traceback


@pytest.mark.unittest
class TestUtilsException:
    def test_str_traceback(self):
        def func1(x):
            return func2(x * 3 + 1)

        def func2(x):
            if x % 2 == 0:
                return func3(x)
            else:
                return func4(x)

        def func3(x):
            raise RuntimeError('this is a runtime error')

        def func4(x):
            raise ValueError('this is a value error')

        try:
            func1(1)
        except Exception as err:
            str_ = str_traceback(err)
            assert 'func1' in str_
            assert 'func2' in str_
            assert 'func3' in str_
            assert 'RuntimeError' in str_
            assert 'this is a runtime error' in str_
            assert 'func4' not in str_
            assert 'ValueError' not in str_
            assert 'this is a value error' not in str_

        try:
            func1(2)
        except Exception as err:
            str_ = str_traceback(err)
            assert 'func1' in str_
            assert 'func2' in str_
            assert 'func3' not in str_
            assert 'RuntimeError' not in str_
            assert 'this is a runtime error' not in str_
            assert 'func4' in str_
            assert 'ValueError' in str_
            assert 'this is a value error' in str_
