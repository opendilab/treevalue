import pytest

from treevalue.tree import jsonify, TreeValue, clone, typetrans, raw


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeService:
    def test_jsonify(self):
        tv1 = TreeValue({'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}})
        assert jsonify(tv1) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert jsonify(tv1.c) == {'x': 2, 'y': 3}

        tv2 = TreeValue({'a': 1, 'b': 2, 'c': raw({'x': 2, 'y': 3})})
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }
        assert tv2.c == {'x': 2, 'y': 3}

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
        tv1.c = TreeValue({'a': 7, 'b': 4})
        assert jsonify(tv1) == {
            'a': 3, 'b': 4, 'c': {'a': 7, 'b': 4}
        }
        assert jsonify(tv2) == {
            'a': 1, 'b': 2, 'c': {'x': 2, 'y': 3}
        }

        tv3 = TreeValue({
            'a': raw({'a': 1, 'b': 2}),
            'b': raw({'a': 3, 'b': 4}),
            'x': {
                'c': raw({'a': 5, 'b': 6}),
                'd': raw({'a': 7, 'b': 8}),
            }
        })

        tv4 = clone(tv3)
        assert tv4 == tv3
        assert tv4.a is tv3.a
        assert tv4.b is tv3.b
        assert tv4.x.c is tv3.x.c
        assert tv4.x.d is tv3.x.d

        tv5 = clone(tv3, copy_value=True)
        assert tv5 == tv3
        assert tv5.a is not tv3.a
        assert tv5.b is not tv3.b
        assert tv5.x.c is not tv3.x.c
        assert tv5.x.d is not tv3.x.d

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
