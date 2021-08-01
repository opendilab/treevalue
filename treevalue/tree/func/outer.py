import warnings
from functools import reduce

from .base import _BaseProcessor


class _OuterProcessor(_BaseProcessor):
    def get_key_set(self, *args, **kwargs):
        return reduce(lambda x, y: x | y, [set(keyset) for index, keyset in self._get_key_entries(*args, **kwargs)])

    def check_arguments(self, mode, return_type, inherit,
                        allow_missing, missing_func, subside, rise):
        _BaseProcessor.check_arguments(self, mode, return_type, inherit,
                                       allow_missing, missing_func, subside, rise)
        if not allow_missing:
            warnings.warn(RuntimeWarning("Missing is still not allowed, but this may cause KeyError in outer mode."))
