import pytest

from treevalue import delayed
from treevalue.tree.tree import TreeValue, cleaf
from treevalue.tree.tree.constraint import to_constraint, TypeConstraint, EmptyConstraint, LeafConstraint, \
    ValueConstraint, TreeConstraint


class GreaterThanConstraint(ValueConstraint):
    def __init__(self, v):
        self.value = v

    def _validate_value(self, instance):
        if instance <= self.value:
            raise ValueError(f'Invalid value, greater than {self.value!r} expected but {instance!r} found.')

    def _features(self):
        return self.value

    def _contains(self, other):
        return isinstance(other, GreaterThanConstraint) and self.value >= other.value


# noinspection DuplicatedCode,PyArgumentList,PyTypeChecker
@pytest.mark.unittest
class TestTreeTreeConstraint:
    def test_empty(self):
        c1 = to_constraint(None)
        assert isinstance(c1, EmptyConstraint)
        assert not c1
        assert repr(c1) == "<EmptyConstraint>"

        assert c1 == c1
        assert c1 == EmptyConstraint()
        assert c1 == None
        assert c1 != int

        assert c1 >= None
        assert not (c1 > None)
        assert c1 <= None
        assert not (c1 < None)

        assert c1.equiv(None)
        assert c1.equiv(c1)
        assert not c1.equiv(int)

        c1.validate(1)
        c1.validate(None)
        c1.validate(TreeValue({'a': 1, 'b': {'x': 2, 'y': 3}}))

    def test_type(self):
        c1 = to_constraint(int)
        assert isinstance(c1, TypeConstraint)
        assert c1
        assert repr(c1) == '<TypeConstraint <class \'int\'>>'
        assert c1.type_ == int
        assert c1 == int
        assert c1 == to_constraint(int)

        assert c1 >= object
        assert c1 > object
        assert not (c1 <= object)
        assert not (c1 < object)

        assert c1.equiv(int)
        assert c1.equiv(c1)
        assert not c1.equiv(object)

        assert not (object >= c1)
        assert not (object > c1)
        assert object < c1
        assert object <= c1

        assert not (c1 > int)
        assert not (c1 < int)

        retval, retpath, retcons, reterr = c1.check(1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(1)

        retval, retpath, retcons, reterr = c1.check('dksfj')
        assert not retval
        assert retpath == ()
        assert retcons is c1
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate('dksfj')

        t1 = TreeValue({'a': 1, 'b': {'x': 2, 'y': 3}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(t1)

        t2 = TreeValue({'a': 1, 'b': {'x': 2, 'y': 'fff'}})
        retval, retpath, retcons, reterr = c1.check(t2)
        assert not retval
        assert retpath == ('b', 'y')
        assert retcons is c1
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t2)

    def test_leaf(self):
        c1 = to_constraint(cleaf())
        assert isinstance(c1, LeafConstraint)
        assert c1
        assert repr(c1) == '<LeafConstraint>'
        assert c1 == c1
        assert c1 == to_constraint(cleaf())
        assert c1 == cleaf()

        assert c1 >= c1
        assert not (c1 > c1)
        assert c1 <= c1
        assert not (c1 < c1)
        assert c1.equiv(c1)
        assert not c1.equiv(int)

        retval, retpath, retcons, reterr = c1.check(1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(1)

        retval, retpath, retcons, reterr = c1.check('nihao')
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate('nihao')

        t1 = TreeValue({'a': 1, 'b': {'x': 2, 'y': 3}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert not retval
        assert retpath == ()
        assert retcons is c1
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t1)

    def test_custom_value(self):
        c1 = GreaterThanConstraint(3)
        assert c1
        assert c1.value == 3
        assert repr(c1) == '<GreaterThanConstraint 3>'
        assert c1 == c1
        assert c1 == GreaterThanConstraint(3)
        assert c1 != GreaterThanConstraint(2)

        assert c1 >= GreaterThanConstraint(3)
        assert not (c1 > GreaterThanConstraint(3))
        assert c1 <= GreaterThanConstraint(3)
        assert not (c1 < GreaterThanConstraint(3))

        assert c1.equiv(c1)
        assert c1.equiv(GreaterThanConstraint(3))
        assert not c1.equiv(GreaterThanConstraint(2))
        assert not c1.equiv(GreaterThanConstraint(4))

        assert c1 >= GreaterThanConstraint(2)
        assert c1 > GreaterThanConstraint(2)
        assert not (c1 <= GreaterThanConstraint(2))
        assert not (c1 < GreaterThanConstraint(2))

        assert not (c1 >= GreaterThanConstraint(4))
        assert not (c1 > GreaterThanConstraint(4))
        assert c1 <= GreaterThanConstraint(4)
        assert c1 < GreaterThanConstraint(4)

        retval, retpath, retcons, reterr = c1.check(10)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(10)

        retval, retpath, retcons, reterr = c1.check(3)
        assert not retval
        assert retpath == ()
        assert retcons is c1
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(3)

        retval, retpath, retcons, reterr = c1.check(2)
        assert not retval
        assert retpath == ()
        assert retcons is c1
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(2)

        t1 = TreeValue({'a': 10, 'b': {'x': 4, 'y': 5}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(t1)

        t1 = TreeValue({'a': 10, 'b': {'x': 3, 'y': 5}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert not retval
        assert retpath == ('b', 'x')
        assert retcons is c1
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(t1)

        t1 = TreeValue({'a': 10, 'b': {'x': 4, 'y': 2}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert not retval
        assert retpath == ('b', 'y')
        assert retcons is c1
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(t1)

    def test_composite(self):
        c1 = to_constraint([
            GreaterThanConstraint(3),
            int
        ])
        assert c1
        assert repr(c1) == "<CompositeConstraint (<GreaterThanConstraint 3>, <TypeConstraint <class 'int'>>)>"

        assert c1 == to_constraint([int, int, GreaterThanConstraint(3)])
        assert c1 == to_constraint([int, int, GreaterThanConstraint(3), GreaterThanConstraint(0)])
        assert c1 == to_constraint(
            [int, [int, GreaterThanConstraint(3), [EmptyConstraint()]], GreaterThanConstraint(0)])

        assert to_constraint([]) == EmptyConstraint()
        assert to_constraint([None]) == EmptyConstraint()
        assert to_constraint([int, int]) == int

        assert c1 >= c1
        assert not (c1 > c1)
        assert c1 <= c1
        assert not (c1 < c1)

        assert c1 >= int
        assert c1 > int
        assert not (c1 <= int)
        assert not (c1 < int)

        assert c1 >= GreaterThanConstraint(3)
        assert c1 > GreaterThanConstraint(3)
        assert not (c1 <= GreaterThanConstraint(3))
        assert not (c1 < GreaterThanConstraint(3))

        assert c1 >= GreaterThanConstraint(2)
        assert c1 > GreaterThanConstraint(2)
        assert not (c1 <= GreaterThanConstraint(2))
        assert not (c1 < GreaterThanConstraint(2))

        assert not (c1 >= GreaterThanConstraint(4))
        assert not (c1 > GreaterThanConstraint(4))
        assert not (c1 <= GreaterThanConstraint(4))
        assert not (c1 < GreaterThanConstraint(4))

        assert c1 >= [int, GreaterThanConstraint(3)]
        assert not (c1 > [int, GreaterThanConstraint(3)])
        assert c1 <= [int, GreaterThanConstraint(3)]
        assert not (c1 < [int, GreaterThanConstraint(3)])

        assert c1 >= [int, GreaterThanConstraint(2)]
        assert c1 > [int, GreaterThanConstraint(2)]
        assert not (c1 <= [int, GreaterThanConstraint(2)])
        assert not (c1 < [int, GreaterThanConstraint(2)])

        assert not (c1 >= [int, GreaterThanConstraint(4)])
        assert not (c1 > [int, GreaterThanConstraint(4)])
        assert c1 <= [int, GreaterThanConstraint(4)]
        assert c1 < [int, GreaterThanConstraint(4)]

        assert c1 >= [object, GreaterThanConstraint(2)]
        assert c1 > [object, GreaterThanConstraint(2)]
        assert not (c1 <= [object, GreaterThanConstraint(2)])
        assert not (c1 < [object, GreaterThanConstraint(2)])

        retval, retpath, retcons, reterr = c1.check(10)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(10)

        retval, retpath, retcons, reterr = c1.check(10.0)
        assert not retval
        assert retpath == ()
        assert retcons == int
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(10.0)

        retval, retpath, retcons, reterr = c1.check(2)
        assert not retval
        assert retpath == ()
        assert retcons == GreaterThanConstraint(3)
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(2)

        t1 = TreeValue({'a': 10, 'b': {'x': 5, 'y': 4}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(t1)

        t2 = TreeValue({'a': 10.0, 'b': {'x': 5, 'y': 4}})
        retval, retpath, retcons, reterr = c1.check(t2)
        assert not retval
        assert retpath == ('a',)
        assert retcons == int
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t2)

        t3 = TreeValue({'a': 10, 'b': {'x': 1, 'y': 4}})
        retval, retpath, retcons, reterr = c1.check(t3)
        assert not retval
        assert retpath == ('b', 'x')
        assert retcons == GreaterThanConstraint(3)
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(t3)

        t4 = TreeValue({'a': 10, 'b': {'x': 5, 'y': 4.1}})
        retval, retpath, retcons, reterr = c1.check(t4)
        assert not retval
        assert retpath == ('b', 'y')
        assert retcons == int
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t4)

    def test_tree(self):
        assert to_constraint({'a': None, 'b': []}) == to_constraint(None)

        c1 = to_constraint({
            'a': [int, GreaterThanConstraint(3)],
            'b': {
                'x': [cleaf(), str, None],
                'y': float,
            },
            'c': None,
        })
        assert c1
        assert c1 == {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}

        assert c1 >= c1
        assert not (c1 > c1)
        assert c1 <= c1
        assert not (c1 < c1)

        assert not (c1 >= object)
        assert not (c1 > object)
        assert not (c1 <= object)
        assert not (c1 < object)

        assert c1 >= {'a': int}
        assert c1 > {'a': int}
        assert not (c1 <= {'a': int})
        assert not (c1 < {'a': int})

        assert c1 >= {'a': int, 'b': {'y': float}}
        assert c1 > {'a': int, 'b': {'y': float}}
        assert not (c1 <= {'a': int, 'b': {'y': float}})
        assert not (c1 < {'a': int, 'b': {'y': float}})

        assert c1 >= {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}
        assert not (c1 > {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}})
        assert c1 <= {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}
        assert not (c1 < {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}})

        assert c1 >= {'c': None}
        assert c1 > {'c': None}
        assert not (c1 <= {'c': None})
        assert not (c1 < {'c': None})

        retval, retpath, retcons, reterr = c1.check(1)
        assert not retval
        assert retpath == ()
        assert retcons == {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(1)

        t1 = TreeValue({'a': 10, 'b': {'x': 'abc', 'y': 3.5}})
        retval, retpath, retcons, reterr = c1.check(t1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(t1)

        t2 = TreeValue({'a': 10.1, 'b': {'x': 'abc', 'y': 3.5}})
        retval, retpath, retcons, reterr = c1.check(t2)
        assert not retval
        assert retpath == ('a',)
        assert retcons == int
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t2)

        t3 = TreeValue({'a': 1, 'b': {'x': 'abc', 'y': 3.5}})
        retval, retpath, retcons, reterr = c1.check(t3)
        assert not retval
        assert retpath == ('a',)
        assert retcons == GreaterThanConstraint(3)
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(t3)

        t4 = TreeValue({'a': 10, 'b': {'x': 123, 'y': 3.5}})
        retval, retpath, retcons, reterr = c1.check(t4)
        assert not retval
        assert retpath == ('b', 'x')
        assert retcons == str
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t4)

        t5 = TreeValue({'a': 10, 'b': {'x': {'f': '123', }, 'y': 3.5}})
        retval, retpath, retcons, reterr = c1.check(t5)
        assert not retval
        assert retpath == ('b', 'x')
        assert retcons == cleaf()
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t5)

        t6 = TreeValue({'a': 10, 'b': {'x': 'abc', 'y': {'f': 28.3, 'g': 14.0}}})
        retval, retpath, retcons, reterr = c1.check(t6)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(t6)

        t7 = TreeValue({'a': 10, 'b': {'x': 'abc', 'y': {'f': 28.3, 'g': 14}}})
        retval, retpath, retcons, reterr = c1.check(t7)
        assert not retval
        assert retpath == ('b', 'y', 'g')
        assert retcons == float
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(t7)

    def test_composite_tree(self):
        c1 = to_constraint([
            {
                'a': [int, object],
                'b': {
                    'x': [str, None],
                    'y': object,
                },
                'c': None,
            },
            {
                'b': {
                    'x': [cleaf(), None],
                    'y': float,
                }
            },
            {
                'a': GreaterThanConstraint(3),
            },
        ])
        assert c1
        assert isinstance(c1, TreeConstraint)
        assert c1 == {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}

        assert c1 >= c1
        assert not (c1 > c1)
        assert c1 <= c1
        assert not (c1 < c1)

        assert not (c1 >= object)
        assert not (c1 > object)
        assert not (c1 <= object)
        assert not (c1 < object)

        assert c1 >= {'a': int}
        assert c1 > {'a': int}
        assert not (c1 <= {'a': int})
        assert not (c1 < {'a': int})

        assert c1 >= {'a': int, 'b': {'y': float}}
        assert c1 > {'a': int, 'b': {'y': float}}
        assert not (c1 <= {'a': int, 'b': {'y': float}})
        assert not (c1 < {'a': int, 'b': {'y': float}})

        assert c1 >= {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}
        assert not (c1 > {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}})
        assert c1 <= {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}}
        assert not (c1 < {'a': [int, GreaterThanConstraint(3)], 'b': {'x': [cleaf(), str], 'y': float}})

        assert c1 >= {'c': None}
        assert c1 > {'c': None}
        assert not (c1 <= {'c': None})
        assert not (c1 < {'c': None})

    def test_complex(self):
        c1 = to_constraint([
            GreaterThanConstraint(4),
            {
                'a': [int, object],
                'b': {
                    'x': [int, None],
                    'y': object,
                },
                'c': None,
            },
            {
                'b': {
                    'x': [cleaf(), None],
                    'y': int,
                }
            },
            {
                'a': GreaterThanConstraint(3),
            },
        ])
        assert c1 == [
            GreaterThanConstraint(4),
            {
                'a': [int, GreaterThanConstraint(3)],
                'b': {
                    'x': [int, cleaf()],
                    'y': int,
                }
            },
        ]

    def test_with_delay(self):
        c1 = to_constraint([
            object,
            {
                'a': [int, GreaterThanConstraint(3)],
                'b': {
                    'x': [cleaf(), str, None],
                    'y': float,
                },
                'c': None,
            }
        ])

        t1 = TreeValue({
            'a': delayed(lambda x, y: x * (y + 1), 3, 6),
            'b': delayed(lambda x: TreeValue({
                'x': f'f-{x * x!r}',
                'y': x * 1.1,
            }), x=7)
        })
        retval, retpath, retcons, reterr = c1.check(t1)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None

        t2 = TreeValue({
            'a': delayed(lambda x, y: x * (y + 1), 3, 6),
            'b': delayed(lambda x: TreeValue({
                'x': x * x,
                'y': x * 1.1,
            }), x=7)
        })
        retval, retpath, retcons, reterr = c1.check(t2)
        assert not retval
        assert retpath == ('b', 'x')
        assert retcons == str
        assert isinstance(reterr, TypeError)

        t2 = TreeValue({
            'a': delayed(lambda x, y: x * (y + 1), 3, -6),
            'b': delayed(lambda x: TreeValue({
                'x': f'f-{x * x!r}',
                'y': x * 1.1,
            }), x=7)
        })
        retval, retpath, retcons, reterr = c1.check(t2)
        assert not retval
        assert retpath == ('a',)
        assert retcons == GreaterThanConstraint(3)
        assert isinstance(reterr, ValueError)
