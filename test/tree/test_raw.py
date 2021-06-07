import pytest

from treevalue.tree import RawPackage, raw_value, raw_unpack


@pytest.mark.unittest
class TestTreeRaw:
    def test_raw_package(self):
        rp = RawPackage(1)
        assert rp.value == 1

        with pytest.raises(TypeError):
            class _SubClass(RawPackage):
                pass

    def test_raw_value(self):
        v = 1
        rv = raw_value(v)
        assert isinstance(rv, RawPackage)
        assert rv.value == 1

        rv2 = raw_value(rv)
        assert isinstance(rv2, RawPackage)
        assert rv2 is rv
        assert rv2.value == 1

    def test_raw_unpack(self):
        v = 1
        rv = raw_value(v)
        rv2 = raw_value(rv)

        assert raw_unpack(rv2) == 1
        assert raw_unpack(rv) == 1
        assert raw_unpack(1) == 1
