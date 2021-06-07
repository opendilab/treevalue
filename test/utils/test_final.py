import pytest

from treevalue.utils.final import FinalMeta


@pytest.mark.unittest
class TestUtilsFinal:
    def test_final_meta(self):
        class _FinalClass(metaclass=FinalMeta):
            pass

        assert isinstance(_FinalClass(), _FinalClass)

        with pytest.raises(TypeError):
            class _InvalidClass(_FinalClass):
                pass
