from abc import ABCMeta, abstractmethod
from typing import List


class BaseTree(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError  # pragma: no cover

    def json(self):
        return {
            key: value.json() if isinstance(value, BaseTree) else value
            for key, value in self.items()
        }

    @abstractmethod
    def view(self, path: List[str]):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def clone(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def items(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def keys(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def values(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def actual(self):
        raise NotImplementedError  # pragma: no cover

    def __len__(self):
        return len(self.keys())

    def __hash__(self):
        return hash(tuple([(key, value) for key, value in sorted(self.items())]))

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, BaseTree):
            if set(self.keys()) == set(other.keys()):
                for key in self.keys():
                    if self[key] != other[key]:
                        return False
                return True
            else:
                return False
        else:
            return False

    def __repr__(self):
        return '<{cls} {id} keys: {keys}>'.format(
            cls=self.__class__.__name__,
            id=hex(id(self.actual())),
            keys=repr(sorted(self.keys()))
        )
