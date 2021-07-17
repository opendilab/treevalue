from treevalue.utils import args_iter


def _find_keys(*args, **kwargs):
    from ...tree import TreeValue

    def _iter_items():
        for _index, _item in args_iter(*args, **kwargs):
            if isinstance(_item, TreeValue):
                yield _index, set(_item.keys())
