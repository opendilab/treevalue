import pytest

from treevalue.utils import seed_random


@pytest.mark.unittest
class TestUtilsRandom:
    def test_seed_random(self):
        with seed_random(0) as rnd:
            a, b, c = rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff)
        assert (a, b, c) == (197, 215, 20)

        with seed_random(233) as rnd:
            a, b, c = rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff)
        assert (a, b, c) == (89, 118, 247)
