from itertools import chain

from ..tree.tree import get_data_property, TreeValue


def get_key_entries(*args, **kwargs):
    return [
        (index, tuple(sorted(get_data_property(value).keys())))
        for index, value in chain(enumerate(args), kwargs.items())
        if isinstance(value, TreeValue)
    ]
