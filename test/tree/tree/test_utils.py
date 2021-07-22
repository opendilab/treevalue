import pytest

from treevalue.tree import jsonify, TreeValue, view, clone, typetrans, mapping


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

    def test_typetrans(self):
        class MyTreeValue(TreeValue):
            pass

        class NonTreeValue:
            pass

        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = typetrans(tv1, MyTreeValue)

        assert tv2 == MyTreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert tv2 != tv1

        with pytest.raises(TypeError):
            typetrans(tv1, NonTreeValue)

    def test_mapping(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        tv2 = mapping(tv1, lambda x: x + 2)

        assert tv2 == TreeValue({'a': 3, 'b': 4, 'c': {'x': 4, 'y': 5}})
