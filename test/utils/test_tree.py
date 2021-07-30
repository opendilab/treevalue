import json

import pytest

from treevalue.utils import build_tree


@pytest.mark.unittest
class TestUtilsTree:
    def test_build_tree(self):
        t = build_tree(
            {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'z': [1, 2], 'v': {'1': '2'}},
            repr_gen=lambda x: '<node>' if isinstance(x, dict) else repr(x),
        )
        assert json.loads(t.to_json(sort=True)) == {'<node>': {
            'children': ["'a' --> 1", "'b' --> 2", {"'v' --> <node>": {'children': ["'1' --> '2'"]}},
                         {"'x' --> <node>": {'children': ["'c' --> 3", "'d' --> 4"]}}, "'z' --> [1, 2]"]}}
