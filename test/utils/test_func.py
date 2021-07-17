import pytest

from treevalue.utils import args_iter


@pytest.mark.unittest
class TestUtilsFunc:
    def test_args_iter(self):
        assert list(args_iter(1, 2, 3, a=1, c=3, b=4)) == [(0, 1), (1, 2), (2, 3), ('a', 1), ('b', 4), ('c', 3)]
