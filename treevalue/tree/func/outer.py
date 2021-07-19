from functools import reduce

from .base import get_key_entries


def get_key_set(*args, **kwargs):
    return reduce(lambda x, y: x | y, [set(keyset) for index, keyset in get_key_entries(*args, **kwargs)])
