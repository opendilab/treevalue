import unittest
from shutil import which
from unittest.mock import patch

import pytest
from hbutils.testing import cmdv

from treevalue.utils import build_graph


@pytest.fixture()
def no_dot():
    def _no_dot_which(x):
        if x == 'dot':
            return None
        else:
            return which(x)

    with patch('shutil.which', _no_dot_which):
        yield


@pytest.mark.unittest
class TestUtilsTree:
    @unittest.skipUnless(cmdv('dot'), 'Dot installed only')
    def test_build_graph(self):
        t = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
        g = build_graph((t, 't'), graph_title="Demo of build_graph.")
        assert "Demo of build_graph." in g.source
        assert "t.x" in g.source
        assert len(g.source) <= 560

        g2 = build_graph(t, graph_title="Demo 2 of build_graph.")
        assert "Demo 2 of build_graph." in g2.source
        assert "root_0" in g2.source
        assert len(g2.source) <= 580

        g3 = build_graph((t,), graph_title="Demo 3 of build_graph.")
        assert "Demo 3 of build_graph." in g3.source
        assert "root_0" in g3.source
        assert len(g3.source) <= 580

        g4 = build_graph((), graph_title="Demo 4 of build_graph.")
        assert "Demo 4 of build_graph." in g4.source
        assert "node" not in g4.source
        assert len(g4.source) <= 110

    def test_build_graph_without_dot(self, no_dot):
        t = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
        with pytest.raises(EnvironmentError):
            _ = build_graph((t, 't'), graph_title="Demo of build_graph.")
