import pytest

from treevalue.utils import StaticValueProxy, ValueProxy


@pytest.mark.unittest
class TestUtilsValue:
    def test_static_value_proxy(self):
        sp = StaticValueProxy(1)
        assert sp.value == 1
        assert repr(sp) == '<StaticValueProxy value: 1>'
        with pytest.raises(AttributeError):
            sp.value = 2

    def test_value_proxy(self):
        p = ValueProxy(1)
        assert p.value == 1
        assert repr(p) == '<ValueProxy value: 1>'

        p.value = 2
        assert p.value == 2
        assert repr(p) == '<ValueProxy value: 2>'
