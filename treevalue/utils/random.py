import random
from contextlib import contextmanager
from datetime import datetime
from random import Random


@contextmanager
def seed_random(seed):
    """
    Overview:
        Get seeded random object in a `with` block.

    Arguments:
        - seed (:obj:`int`): Random seed, should be a `int`.
    """
    rnd = Random()
    rnd.seed(seed)
    try:
        yield rnd
    finally:
        rnd.seed()


def random_hex(length: int = 32) -> str:
    """
    Overview:
        Generate random hex string.

    Arguments:
        - length (:obj:`int`): Length of hex string, default is `32`.

    Returns:
        - string (:obj:`str`): Generated string.

    Examples:
        >>> random_hex()  # 'ca7f14b25aa4498efdacb54e9ff72784'
    """
    return ''.join([hex(random.randint(0, 15))[2:] for _ in range(length)])


def random_hex_with_timestamp(length: int = 12) -> str:
    """
    Overview:
        Generate random hex string, with prefix of timestamp.

    Arguments:
        - length (:obj:`int`): Length of hex string, default is `12`.

    Returns:
        - string (:obj:`str`): Generated string.

    Examples:
        >>> random_hex_with_timestamp()  # '20210729_202059576266_69603d64afad'
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + random_hex(length)
