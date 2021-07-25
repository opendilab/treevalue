import warnings

from .base import _BaseProcessor


class _StrictProcessor(_BaseProcessor):
    def get_key_set(self, *args, **kwargs):
        key_entries = self._get_key_entries(*args, **kwargs)
        first_index, first_keyset = key_entries[0]
        for index, keyset in key_entries[1:]:
            if keyset != first_keyset:
                raise KeyError(
                    "Argument keys not match in strict mode, key set of argument {a1} is {ks1} but {a2} in {ks2}.".format(
                        a1=repr(first_index), ks1=repr(first_keyset),
                        a2=repr(index), ks2=repr(keyset),
                    ))

        return first_keyset

    def check_arguments(self, mode, return_type, inherit,
                        allow_missing, missing_func, subside, rise):
        _BaseProcessor.check_arguments(self, mode, return_type, inherit,
                                       allow_missing, missing_func, subside, rise)
        if allow_missing:
            warnings.warn(RuntimeWarning("Allow missing detected, but cannot applied in strict mode."))
