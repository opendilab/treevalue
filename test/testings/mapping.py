import collections.abc


class CustomMapping(collections.abc.Mapping):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getitem__(self, __key):
        return self._kwargs[__key]

    def __len__(self):
        return len(self._kwargs)

    def __iter__(self):
        yield from self._kwargs
