import pickle

import pytest

from treevalue.tree.common import raw, unraw, RawWrapper


@pytest.mark.unittest
class TestTreeBase:
    def test_raw(self):
        assert raw(1) == 1
        assert raw('sdklfgj') == 'sdklfgj'

        h = {'a': 1, 'b': 2}
        r = raw(h)
        assert isinstance(r, RawWrapper)
        assert r.value() is h

    def test_unraw(self):
        assert unraw(1) == 1
        assert unraw('sdklfgj') == 'sdklfgj'

        h = {'a': 1, 'b': 2}
        r = raw(h)
        u = unraw(r)
        assert u is h

    def test_pickle(self):
        h = {'a': 1, 'b': 2}
        r = raw(h)

        bt = pickle.dumps(r)
        nt = pickle.loads(bt)

        assert isinstance(nt, RawWrapper)
        assert nt.value() == h
