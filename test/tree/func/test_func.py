import pytest

from treevalue.tree import TreeMode, func_treelize, TreeValue


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeFuncFunc:
    def test_tree_mode(self):
        assert TreeMode.loads(1) == TreeMode.STRICT
        assert TreeMode.loads(2) == TreeMode.LEFT
        assert TreeMode.loads(3) == TreeMode.INNER
        assert TreeMode.loads(4) == TreeMode.OUTER
        assert TreeMode.loads('strict') == TreeMode.STRICT
        assert TreeMode.loads('LEFT') == TreeMode.LEFT
        assert TreeMode.loads('Inner') == TreeMode.INNER
        assert TreeMode.loads('OuTeR') == TreeMode.OUTER
        assert TreeMode.loads(TreeMode.STRICT) == TreeMode.STRICT
        assert TreeMode.loads(TreeMode.LEFT) == TreeMode.LEFT
        assert TreeMode.loads(TreeMode.INNER) == TreeMode.INNER
        assert TreeMode.loads(TreeMode.OUTER) == TreeMode.OUTER

    def test_tree_value_type(self):
        class _MyTreeValue(TreeValue):
            pass

        @func_treelize(return_type=_MyTreeValue)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        tr1 = ssum(t1, t2)
        assert tr1 != TreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert tr1 == _MyTreeValue({'a': 12, 'b': 24, 'x': {'c': 36, 'd': 48}})
        assert isinstance(tr1, _MyTreeValue)
        assert isinstance(tr1.x, _MyTreeValue)

    def test_tree_value_type_none(self):
        @func_treelize(return_type=None)
        def ssum(*args):
            return sum(args)

        t1 = TreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
        t2 = TreeValue({'a': 11, 'b': 22, 'x': {'c': 33, 'd': 44}})
        tr1 = ssum(t1, t2)
        assert tr1 is None

    def test_tree_value_type_invalid(self):
        class _MyTreeValue:
            pass

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            @func_treelize(return_type=_MyTreeValue)
            def ssum(*args):
                return sum(args)

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            @func_treelize(return_type=233)
            def ssum(*args):
                return sum(args)
