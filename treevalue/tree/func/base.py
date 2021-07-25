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

    def check_arguments(self, mode, return_type, inherit, allow_missing, missing_func, subside, rise):
        if return_type is not None:
            if not isinstance(return_type, type):
                raise TypeError("Return type should be a type or none, but {type} found.".format(
                    type=repr(type(return_type).__name__)))
            elif not issubclass(return_type, TreeValue):
                raise TypeError("Tree value should be subclass of TreeValue, but {type} found.".format(
                    type=repr(return_type.__name__)
                ))
