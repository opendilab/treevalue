import pytest

from treevalue.tree import general_tree_value, method_treelize
from .base import get_fasttreevalue_test


class TreeNumber(general_tree_value()):
    @method_treelize()
    def append(self, *args):
        return sum([self, *args])


class NonDefaultTreeNumber(general_tree_value(base=dict(), methods=dict(
    __add__=dict(missing=0, mode='outer'),
    __radd__=dict(missing=0, mode='outer'),
))):
    pass


class BanAndOverrideTreeNumber(general_tree_value(methods=dict(
    __add__=NotImplemented,
    __radd__=NotImplemented,
    __iadd__=NotImplemented,
    __mul__=KeyError("lksdjfkl"),
    __rmul__=KeyError("lsdfjkldks"),
    __imul__=KeyError("dklfgjsl"),
    __matmul__=KeyError,
    __rmatmul__=KeyError,
    __imatmul__=KeyError,
    __pos__=(lambda sp: sp // 2),
    __truediv__=(lambda sp: sp - 2),
))):
    pass


@pytest.mark.unittest
class TestTreeGeneralGeneral(get_fasttreevalue_test(TreeNumber)):
    def test_numeric_append(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 5}})
        t3 = TreeNumber({'a': 11, 'b': 22, 'x': 7})

        assert t1.append(t2, 3) == TreeNumber({'a': 15, 'b': 27, 'x': {'c': 39, 'd': 12}})
        assert t1.append(t3) == TreeNumber({'a': 12, 'b': 24, 'x': {'c': 10, 'd': 11}})

    def test_default_tree_number(self):
        t1 = TreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 7}})
        t2 = TreeNumber({'a': 11, 'b': 22, 'c': 4, 'x': {'c': 33, 'd': 5}})

        with pytest.raises(KeyError):
            _ = t1 + t2
        with pytest.raises(KeyError):
            _ = t1 - t2

    def test_non_default_tree_number(self):
        t1 = NonDefaultTreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 7}})
        t2 = NonDefaultTreeNumber({'a': 11, 'b': 22, 'c': 4, 'x': {'c': 33, 'd': 5}})

        assert (t1 + t2) == NonDefaultTreeNumber({'a': 12, 'b': 24, 'c': 4, 'x': {'c': 36, 'd': 9, 'e': 7}})
        with pytest.raises(KeyError):
            _ = t1 - t2

    def test_ban_add(self):
        t1 = BanAndOverrideTreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 7}})
        t2 = BanAndOverrideTreeNumber({'a': 11, 'b': 22, 'c': 4, 'x': {'c': 33, 'd': 5}})

        with pytest.raises(TypeError):
            _ = t1 + t2
        with pytest.raises(KeyError):
            _ = t1 * t2
        with pytest.raises(KeyError):
            _ = t1 @ t2
        assert +t1 == BanAndOverrideTreeNumber({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4, 'e': 7}}) // 2
        assert t1 / 3 == BanAndOverrideTreeNumber({'a': 1 - 2, 'b': 2 - 2, 'x': {'c': 3 - 2, 'd': 4 - 2, 'e': 7 - 2}})
