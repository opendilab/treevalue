from functools import partial


def get_property(self, prop):
    if isinstance(prop, str):
        return getattr(self, prop)
    elif hasattr(prop, '__call__'):
        return partial(prop, self)
    else:
        return AttributeError('Unknown property for non-str and non-callable object.')
