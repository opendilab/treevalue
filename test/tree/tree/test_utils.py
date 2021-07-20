import pytest

from treevalue.tree import jsonify, TreeValue, view, clone


@pytest.mark.unittest
class TestTreeTreeUtils:
    def test_jsonify(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert jsonify(tv1.c) == {'x': 2, 'y': 3}

    def test_view(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = view(tv1, ['c'])

        tv2.y = 4
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 4}
        }
        assert jsonify(tv1.c) == {'x': 2, 'y': 4}

        tv1.c = {'a': 2, 'b': 3}
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'a': 2, 'b': 3}
        }
        assert jsonify(tv1.c) == {'a': 2, 'b': 3}

    def test_clone(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = clone(tv1)

        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }

        tv1.a = 3
        tv1.b = 4
        tv1.c = {'a': 7, 'b': 4}
        assert jsonify(tv1) == {
            'a': 3, 'b': 4, 'c': {'a': 7, 'b': 4}
        }
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
