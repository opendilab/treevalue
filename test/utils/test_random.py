import re

import pytest

from treevalue.utils import seed_random, random_hex, random_hex_with_timestamp


@pytest.mark.unittest
class TestUtilsRandom:
    def test_seed_random(self):
        with seed_random(0) as rnd:
            a, b, c = rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff)
        assert (a, b, c) == (197, 215, 20)

        with seed_random(233) as rnd:
            a, b, c = rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff), rnd.randint(0x00, 0xff)
        assert (a, b, c) == (89, 118, 247)

    def test_random_hex(self):
        assert re.fullmatch(r'^[a-f0-9]{32}$', random_hex())
        assert re.fullmatch(r'^[a-f0-9]{48}$', random_hex(48))

    def test_random_hex_with_timestamp(self):
        assert re.fullmatch(r'^\d{8}_\d{12}_[a-f0-9]{12}$', random_hex_with_timestamp())
        assert re.fullmatch(r'^\d{8}_\d{12}_[a-f0-9]{48}$', random_hex_with_timestamp(48))
