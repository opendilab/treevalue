from itertools import chain


def args_iter(*args, **kwargs):
    for _index, _item in chain(enumerate(args), sorted(kwargs.items())):
        yield _index, _item
