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

    def test_raw_safe(self):
        assert raw(1, safe=True) == 1
        assert raw('sdklfgj', safe=True) == 'sdklfgj'

        h = {'a': 1, 'b': 2}
        r = raw(h, safe=True)
        assert isinstance(r, dict)
        assert r == {'__treevalue/raw/wrapper': {'a': 1, 'b': 2}}
        assert r['__treevalue/raw/wrapper'] is h

    def test_double_raw(self):
        h = {'a': 1, 'b': 2}
        r1 = raw(h)
        assert raw(r1) is r1
        assert raw(r1, safe=True) == {'__treevalue/raw/wrapper': {'a': 1, 'b': 2}}

        r2 = raw(h, safe=True)
        assert raw(r2) is r2
        r2x = raw(r2, safe=False)
        assert isinstance(r2x, RawWrapper)
        assert r2x.value() == h

    def test_unraw(self):
        assert unraw(1) == 1
        assert unraw('sdklfgj') == 'sdklfgj'

        h = {'a': 1, 'b': 2}
        r1 = raw(h)
        u = unraw(r1)
        assert u is h

        r2 = raw(h, safe=True)
        assert unraw(r2) is h

    def test_pickle(self):
        h = {'a': 1, 'b': 2}
        r = raw(h)

        bt = pickle.dumps(r)
        nt = pickle.loads(bt)

        assert isinstance(nt, RawWrapper)
        assert nt.value() == h
