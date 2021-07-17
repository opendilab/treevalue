from ....utils import args_iter


def _find_keys(*args, **kwargs):
    from ...tree import TreeValue

    def _find_anchor():
        for _index, _item in args_iter(*args, **kwargs):
            if isinstance(_item, TreeValue):
                return _item
        return None

    _anchor = _find_anchor()
    if _anchor is not None:
        return list(sorted(_anchor.keys()))
    else:
        return None
