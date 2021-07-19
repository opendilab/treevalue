from .base import get_key_entries


def get_key_set(*args, **kwargs):
    key_entries = get_key_entries(*args, **kwargs)
    first_index, first_keyset = key_entries[0]
    for index, keyset in key_entries[1:]:
        if keyset != first_keyset:
            raise KeyError(
                "Argument keys not match in strict mode, key set of argument {a1} is {ks1} but {a2} in {ks2}.".format(
                    a1=repr(first_index), ks1=repr(first_keyset),
                    a2=repr(index), ks2=repr(keyset),
                ))

    return first_keyset
