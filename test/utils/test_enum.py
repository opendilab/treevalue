from enum import IntEnum, Enum

import pytest

from treevalue.utils import int_enum_loads


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestUtilsEnum:
    def test_int_enum_loads_base(self):
        @int_enum_loads()
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        assert Enum1.loads(1) is Enum1.A
        assert Enum1.loads(2) is Enum1.B
        assert Enum1.loads(3) is Enum1.C
        assert Enum1.loads('A') is Enum1.A
        assert Enum1.loads('B') is Enum1.B
        assert Enum1.loads('C') is Enum1.C
        with pytest.raises(TypeError):
            Enum1.loads(None)

    def test_int_enum_loads_error(self):
        with pytest.raises(TypeError):
            @int_enum_loads()
            class Enum1(Enum):
                A = 1
                B = 2
                C = 3

    def test_int_enum_disable_int(self):
        @int_enum_loads(enable_int=False)
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        with pytest.raises(TypeError):
            assert Enum1.loads(1) is Enum1.A
        with pytest.raises(TypeError):
            assert Enum1.loads(2) is Enum1.B
        with pytest.raises(TypeError):
            assert Enum1.loads(3) is Enum1.C
        assert Enum1.loads('A') is Enum1.A
        assert Enum1.loads('B') is Enum1.B
        assert Enum1.loads('C') is Enum1.C
        with pytest.raises(TypeError):
            Enum1.loads(None)

    def test_int_enum_disable_str(self):
        @int_enum_loads(enable_str=False)
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        assert Enum1.loads(1) is Enum1.A
        assert Enum1.loads(2) is Enum1.B
        assert Enum1.loads(3) is Enum1.C
        with pytest.raises(TypeError):
            assert Enum1.loads('A') is Enum1.A
        with pytest.raises(TypeError):
            assert Enum1.loads('B') is Enum1.B
        with pytest.raises(TypeError):
            assert Enum1.loads('C') is Enum1.C
        with pytest.raises(TypeError):
            Enum1.loads(None)

    def test_int_enum_extend_int(self):
        @int_enum_loads(value_preprocess=lambda x: abs(x))
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        assert Enum1.loads(1) is Enum1.A
        assert Enum1.loads(2) is Enum1.B
        assert Enum1.loads(3) is Enum1.C
        assert Enum1.loads(-1) is Enum1.A
        assert Enum1.loads(-2) is Enum1.B
        assert Enum1.loads(-3) is Enum1.C
        assert Enum1.loads('A') is Enum1.A
        assert Enum1.loads('B') is Enum1.B
        assert Enum1.loads('C') is Enum1.C
        with pytest.raises(TypeError):
            Enum1.loads(None)

    def test_int_enum_extend_str(self):
        @int_enum_loads(name_preprocess=lambda x: x.upper())
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        assert Enum1.loads(1) is Enum1.A
        assert Enum1.loads(2) is Enum1.B
        assert Enum1.loads(3) is Enum1.C
        assert Enum1.loads('A') is Enum1.A
        assert Enum1.loads('B') is Enum1.B
        assert Enum1.loads('C') is Enum1.C
        assert Enum1.loads('a') is Enum1.A
        assert Enum1.loads('b') is Enum1.B
        assert Enum1.loads('c') is Enum1.C
        with pytest.raises(TypeError):
            Enum1.loads(None)

    def test_int_enum_extend_else(self):
        @int_enum_loads(external_process=lambda x: None)
        class Enum1(IntEnum):
            A = 1
            B = 2
            C = 3

        assert Enum1.loads(Enum1.A) is Enum1.A
        assert Enum1.loads(Enum1.B) is Enum1.B
        assert Enum1.loads(Enum1.C) is Enum1.C
        assert Enum1.loads(1) is Enum1.A
        assert Enum1.loads(2) is Enum1.B
        assert Enum1.loads(3) is Enum1.C
        assert Enum1.loads('A') is Enum1.A
        assert Enum1.loads('B') is Enum1.B
        assert Enum1.loads('C') is Enum1.C
        assert Enum1.loads(None) is None
        assert Enum1.loads([1, 2]) is None
