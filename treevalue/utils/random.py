from contextlib import contextmanager
from random import Random


@contextmanager
def seed_random(seed):
    """
    Overview:
        Get seeded random object in a `with` block.

    Arguments:
        - seed (:obj:`int`): Random seed, should be a `int`.
    """
    random = Random()
    random.seed(seed)
    try:
        yield random
    finally:
        random.seed()
