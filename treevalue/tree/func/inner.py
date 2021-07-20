from functools import reduce

from .base import _BaseProcessor


class _InnerProcessor(_BaseProcessor):
    def get_key_set(self, *args, **kwargs):
        return reduce(lambda x, y: x & y, [set(keyset) for _, keyset in self._get_key_entries(*args, **kwargs)])

    def check_arguments(self, mode, allow_inherit, allow_missing, missing_value, missing_func):
        pass
