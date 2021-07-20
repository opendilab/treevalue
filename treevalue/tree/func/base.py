from abc import abstractmethod
from itertools import chain

from ..tree.tree import get_data_property, TreeValue
from ...utils import SingletonMeta


class _BaseProcessor(metaclass=SingletonMeta):
    def _get_key_entries(*args, **kwargs):
        return [
            (index, tuple(sorted(get_data_property(value).keys())))
            for index, value in chain(enumerate(args), kwargs.items())
            if isinstance(value, TreeValue)
        ]

    @abstractmethod
    def get_key_set(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def check_arguments(self, mode, allow_inherit, allow_missing, missing_value, missing_func):
        raise NotImplementedError  # pragma: no cover
