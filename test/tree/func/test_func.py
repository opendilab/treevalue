import pytest

from treevalue.tree import TreeMode


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
