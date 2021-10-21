import re

import pytest

from treevalue.utils import random_hex, random_hex_with_timestamp


@pytest.mark.unittest
class TestUtilsRandom:
    def test_random_hex(self):
        assert re.fullmatch(r'^[a-f0-9]{32}$', random_hex())
        assert re.fullmatch(r'^[a-f0-9]{48}$', random_hex(48))

    def test_random_hex_with_timestamp(self):
        assert re.fullmatch(r'^\d{8}_\d{12}_[a-f0-9]{12}$', random_hex_with_timestamp())
        assert re.fullmatch(r'^\d{8}_\d{12}_[a-f0-9]{48}$', random_hex_with_timestamp(48))
