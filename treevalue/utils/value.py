from abc import ABCMeta, abstractmethod


class _ValueProxy(metaclass=ABCMeta):
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._set_value(new_value)

    @abstractmethod
    def _set_value(self, new_value):
        raise NotImplementedError


class StaticValueProxy(_ValueProxy):
    def _set_value(self, new_value):
        raise AttributeError('Unable to set value in {type}.'.format(type=self.__class__.__name__))


class ValueProxy(_ValueProxy):
    def _set_value(self, new_value):
        self._value = new_value
