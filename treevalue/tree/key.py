import re

_KEY_PATTERN = re.compile('^[a-zA-Z_][0-9a-zA-Z_]*$')


def _check_key_format(key):
    if isinstance(key, str):
        if _KEY_PATTERN.fullmatch(key):
            return key
        else:
            raise KeyError('Invalid key, {pattern} expected but {value} found.'.format(
                pattern=repr(_KEY_PATTERN.pattern), value=repr(key),
            ))
    else:
        raise TypeError('String-typed key expected but {type} found.'.format(type=repr(type(key).__name__)))
