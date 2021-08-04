import pickle

import pytest

from treevalue.utils import Color
from ..tests import float_eq


@pytest.mark.unittest
class TestUtilsColor:
    def test_basis(self):
        c1 = Color((0.8, 0.7, 0.5))
        assert float_eq(c1.rgb.red, 0.8)
        assert float_eq(c1.rgb.green, 0.7)
        assert float_eq(c1.rgb.blue, 0.5)
        assert c1.alpha is None
        assert str(c1) == '#ccb280'
        assert repr(c1) == '<Color #ccb280>'

    def test_basic_with_alpha(self):
        c1 = Color((0.8, 0.7, 0.5), 0.6)
        assert float_eq(c1.rgb.red, 0.8)
        assert float_eq(c1.rgb.green, 0.7)
        assert float_eq(c1.rgb.blue, 0.5)
        assert float_eq(c1.alpha, 0.6)
        assert str(c1) == '#ccb28099'
        assert repr(c1) == '<Color #ccb280, alpha: 0.600>'

    def test_basic_with_hex(self):
        c1 = Color('#aabbccdd')
        assert c1.rgb.red == int('aa', 16) / 255
        assert c1.rgb.green == int('bb', 16) / 255
        assert c1.rgb.blue == int('cc', 16) / 255
        assert c1.alpha == int('dd', 16) / 255

        with pytest.raises(ValueError):
            Color('#aabbccd')

        c2 = Color('#aabbccdd', alpha=0.8)
        assert c2.rgb.red == int('aa', 16) / 255
        assert c2.rgb.green == int('bb', 16) / 255
        assert c2.rgb.blue == int('cc', 16) / 255
        assert c2.alpha == int('dd', 16) / 255 * 0.8

    def test_basic_error(self):
        with pytest.raises(TypeError):
            Color(None)

    def test_dumps_hash_and_eq(self):
        c1 = Color('#aabbccdd')
        assert c1 == c1
        assert c1 == Color('#aabbccdd')
        assert pickle.loads(pickle.dumps(c1)) == c1
        assert c1 != 1

        assert hash(Color('#aabbccdd')) == hash(c1)

    def test_set_rgb(self):
        c1 = Color((0.8, 0.7, 0.5), 0.6)
        assert float_eq(c1.rgb.red, 0.8)
        assert float_eq(c1.rgb.green, 0.7)
        assert float_eq(c1.rgb.blue, 0.5)
        assert float_eq(c1.alpha, 0.6)

        r, g, b = c1.rgb
        assert float_eq((r, g, b), (0.8, 0.7, 0.5))
        assert repr(c1.rgb) == '<RGBColorProxy red: 0.800, green: 0.700, blue: 0.500>'

        c1.rgb.red *= 0.7
        c1.rgb.green *= 0.6
        c1.rgb.blue *= 0.8
        c1.alpha *= 0.9
        assert float_eq(c1.rgb.red, 0.56)
        assert float_eq(c1.rgb.green, 0.42)
        assert float_eq(c1.rgb.blue, 0.4)
        assert float_eq(c1.alpha, 0.54)
        assert str(c1) == '#8f6b668a'

    def test_set_hsv(self):
        c1 = Color((0.8, 0.7, 0.5), 0.6)

        h, s, v = c1.hsv
        assert repr(c1.hsv) == '<HSVColorProxy hue: 0.111, saturation: 0.375, value: 0.800>'

        c1.hsv.hue *= 0.6
