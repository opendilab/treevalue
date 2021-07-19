from .base import get_key_entries


def get_key_set(*args, **kwargs):
    key_entries = sorted(
        get_key_entries(*args, **kwargs),
        key=lambda x: (0, x[0]) if isinstance(x[0], int) else (1, x[0])
    )

    _, first_keyset = key_entries[0]
    return first_keyset
