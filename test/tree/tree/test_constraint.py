import pickle

import pytest
import torch

from treevalue import delayed
from treevalue.tree.tree import TreeValue, cleaf
from treevalue.tree.tree.constraint import to_constraint, TypeConstraint, EmptyConstraint, LeafConstraint, \
    ValueConstraint, TreeConstraint, vval, vcheck, nval, ncheck, transact, CompositeConstraint, ValueValidateConstraint, \
    ValueCheckConstraint, NodeCheckConstraint, NodeValidateConstraint


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


class OverValueCheck:
    def __init__(self, value):
        self.value = value

    def __call__(self, v):
        return v > self.value


class OverValueValidation:
    def __init__(self, value):
        self.value = value

    def __call__(self, v):
        if v <= self.value:
            raise ValueError(f'Invalid value - {v!r}.')


# noinspection DuplicatedCode,PyArgumentList,PyTypeChecker
@pytest.mark.unittest
class TestTreeTreeConstraint:
    def test_example_constraint(self):
        c = GreaterThanConstraint(10)
        binary = pickle.dumps(c)
        newc = pickle.loads(binary)

        assert isinstance(newc, GreaterThanConstraint)
        assert newc.value == 10
        assert c == newc

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, EmptyConstraint)

    def test_type_with_meta(self):
        c1 = to_constraint(torch.Tensor)
        assert isinstance(c1, TypeConstraint)
        assert c1
        assert c1.type_ == torch.Tensor

        assert c1 == torch.Tensor
        assert c1 >= torch.Tensor
        assert c1 <= torch.Tensor
        assert not (c1 != torch.Tensor)
        assert not (c1 > torch.Tensor)
        assert not (c1 < torch.Tensor)

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, TypeConstraint)
        assert newc.type_ == int
        assert newc == int

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, LeafConstraint)

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, CompositeConstraint)
        assert newc == [GreaterThanConstraint(3), int]

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, TreeConstraint)
        assert newc == {
            'a': [int, GreaterThanConstraint(3)],
            'b': {
                'x': [cleaf(), str, None],
                'y': float,
            },
            'c': None,
        }

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, TreeConstraint)
        assert newc == [
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
        ]

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

        binary = pickle.dumps(c1)
        newc = pickle.loads(binary)
        assert isinstance(newc, CompositeConstraint)
        assert newc == [
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

    def test_value_func(self):
        def _v_validate(x):
            if x < 5:
                raise ValueError('X is lower than 5.')

        c1 = vval(_v_validate, '5_check')
        assert repr(c1) == '<ValueValidateConstraint 5_check>'
        assert c1 == vval(_v_validate, '5_check')
        assert c1 != vval(_v_validate, '6_check')

        assert c1 >= vval(_v_validate, '5_check')
        assert not (c1 > vval(_v_validate, '5_check'))
        assert c1 <= vval(_v_validate, '5_check')
        assert not (c1 < vval(_v_validate, '5_check'))

        assert c1 >= vval(_v_validate, '4_check')
        assert not (c1 > vval(_v_validate, '4_check'))
        assert c1 <= vval(_v_validate, '4_check')
        assert not (c1 < vval(_v_validate, '4_check'))

        assert c1.equiv(vval(_v_validate, '5_check'))
        assert c1.equiv(vval(_v_validate, '4_check'))
        assert not c1.equiv(vval(int))

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

        _f_check = lambda x: x >= 5
        c2 = vcheck(_f_check, '5_check')
        assert repr(c2) == '<ValueCheckConstraint 5_check>'
        assert c2 == c2
        assert c2 == vcheck(_f_check, '5_check')
        assert c2 != vcheck(_f_check, '4_check')

        assert c2 >= vcheck(_f_check, '5_check')
        assert not (c2 > vcheck(_f_check, '5_check'))
        assert c2 <= vcheck(_f_check, '5_check')
        assert not (c2 < vcheck(_f_check, '5_check'))

        assert c2 >= vcheck(_f_check, '4_check')
        assert not (c2 > vcheck(_f_check, '4_check'))
        assert c2 <= vcheck(_f_check, '4_check')
        assert not (c2 < vcheck(_f_check, '4_check'))

        assert c2.equiv(vcheck(_f_check, '5_check'))
        assert c2.equiv(vcheck(_f_check, '5_check'))
        assert not c2.equiv(vcheck(lambda x: x >= 4, '5_check'))

        retval, retpath, retcons, reterr = c2.check(10)
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c2.validate(10)

        retval, retpath, retcons, reterr = c2.check(3)
        assert not retval
        assert retpath == ()
        assert retcons is c2
        assert isinstance(reterr, AssertionError)
        with pytest.raises(AssertionError):
            c2.validate(3)

        cx = vval(OverValueValidation(5), 'over5')
        binary = pickle.dumps(cx)
        newcx = pickle.loads(binary)
        assert isinstance(newcx, ValueValidateConstraint)
        assert isinstance(newcx.func, OverValueValidation)
        assert newcx.func.value == 5
        assert newcx.name == 'over5'

        cx = vcheck(OverValueCheck(5), 'over5')
        binary = pickle.dumps(cx)
        newcx = pickle.loads(binary)
        assert isinstance(newcx, ValueCheckConstraint)
        assert isinstance(newcx.func, OverValueCheck)
        assert newcx.func.value == 5
        assert newcx.name == 'over5'

    def test_node_func(self):
        def _n_validate(x: TreeValue):
            if 'a' in x and 'b' in x:
                if x.a + x.b <= 5:
                    raise ValueError('A + B is lower than 5.')
            else:
                raise KeyError('A or B not found.')

        c1 = nval(_n_validate, 'ab5')
        assert repr(c1) == '<NodeValidateConstraint ab5>'
        assert c1 == c1
        assert c1 == nval(_n_validate, 'ab5')
        assert c1 != nval(_n_validate, 'ab6')

        assert c1 >= nval(_n_validate, 'ab5')
        assert not (c1 > nval(_n_validate, 'ab5'))
        assert c1 <= nval(_n_validate, 'ab5')
        assert not (c1 < nval(_n_validate, 'ab5'))

        assert c1 >= nval(_n_validate, 'ab6')
        assert not (c1 > nval(_n_validate, 'ab6'))
        assert c1 <= nval(_n_validate, 'ab6')
        assert not (c1 < nval(_n_validate, 'ab6'))

        retval, retpath, retcons, reterr = c1.check(TreeValue({'a': 4, 'b': 2}))
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c1.validate(TreeValue({'a': 4, 'b': 2}))

        retval, retpath, retcons, reterr = c1.check(TreeValue({'a': 2, 'b': 2}))
        assert not retval
        assert retpath == ()
        assert retcons == nval(_n_validate, 'ab5')
        assert isinstance(reterr, ValueError)
        with pytest.raises(ValueError):
            c1.validate(TreeValue({'a': 2, 'b': 2}))

        retval, retpath, retcons, reterr = c1.check(TreeValue({'b': 2}))
        assert not retval
        assert retpath == ()
        assert retcons == nval(_n_validate, 'ab5')
        assert isinstance(reterr, KeyError)
        with pytest.raises(KeyError):
            c1.validate(TreeValue({'b': 2}))

        retval, retpath, retcons, reterr = c1.check(10)
        assert not retval
        assert retpath == ()
        assert retcons == nval(_n_validate, 'ab5')
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c1.validate(10)

        _f_check = lambda x: 'a' in x and 'b' in x and x.a + x.b > 5
        c2 = ncheck(_f_check, 'ab5')
        assert repr(c2) == '<NodeCheckConstraint ab5>'
        assert c2 == c2
        assert c2 == ncheck(_f_check, 'ab5')
        assert c2 != ncheck(_f_check, 'ab6')

        assert c2 >= ncheck(_f_check, 'ab5')
        assert not (c2 > ncheck(_f_check, 'ab5'))
        assert c2 <= ncheck(_f_check, 'ab5')
        assert not (c2 < ncheck(_f_check, 'ab5'))

        assert c2 >= ncheck(_f_check, 'ab6')
        assert not (c2 > ncheck(_f_check, 'ab6'))
        assert c2 <= ncheck(_f_check, 'ab6')
        assert not (c2 < ncheck(_f_check, 'ab6'))

        retval, retpath, retcons, reterr = c2.check(TreeValue({'a': 4, 'b': 2}))
        assert retval
        assert retpath is None
        assert retcons is None
        assert reterr is None
        c2.validate(TreeValue({'a': 4, 'b': 2}))

        retval, retpath, retcons, reterr = c2.check(TreeValue({'a': 2, 'b': 2}))
        assert not retval
        assert retpath == ()
        assert retcons == ncheck(_f_check, 'ab5')
        assert isinstance(reterr, AssertionError)
        with pytest.raises(AssertionError):
            c2.validate(TreeValue({'a': 2, 'b': 2}))

        retval, retpath, retcons, reterr = c2.check(TreeValue({'b': 2}))
        assert not retval
        assert retpath == ()
        assert retcons == ncheck(_f_check, 'ab5')
        assert isinstance(reterr, AssertionError)
        with pytest.raises(AssertionError):
            c2.validate(TreeValue({'b': 2}))

        retval, retpath, retcons, reterr = c2.check(10)
        assert not retval
        assert retpath == ()
        assert retcons == ncheck(_f_check, 'ab5')
        assert isinstance(reterr, TypeError)
        with pytest.raises(TypeError):
            c2.validate(10)

        cx = nval(OverValueValidation(5), 'over5')
        binary = pickle.dumps(cx)
        newcx = pickle.loads(binary)
        assert isinstance(newcx, NodeValidateConstraint)
        assert isinstance(newcx.func, OverValueValidation)
        assert newcx.func.value == 5
        assert newcx.name == 'over5'

        cx = ncheck(OverValueCheck(5), 'over5')
        binary = pickle.dumps(cx)
        newcx = pickle.loads(binary)
        assert isinstance(newcx, NodeCheckConstraint)
        assert isinstance(newcx.func, OverValueCheck)
        assert newcx.func.value == 5
        assert newcx.name == 'over5'

    def test_hash_eq(self):
        d = {
            to_constraint(int): 2389,
            to_constraint(GreaterThanConstraint(3)): 'sdfk'
        }

        assert to_constraint(int) in d
        assert d[to_constraint(int)] == 2389
        assert to_constraint(float) not in d
        assert GreaterThanConstraint(3) in d
        assert d[GreaterThanConstraint(3)] == 'sdfk'
        assert GreaterThanConstraint(4) not in d

    def test_error(self):
        with pytest.raises(TypeError):
            _ = to_constraint('jkdhfkjsdfh')

    def test_transact(self):
        assert transact(int, 'a') == int
        assert transact(nval(lambda x: True, 'nothing'), 'b') == None
        assert transact({'a': int, 'b': [float, GreaterThanConstraint(3)]}, 'a') == int
        assert transact({'a': int, 'b': [float, GreaterThanConstraint(3)]}, 'b') == [float, GreaterThanConstraint(3)]
        assert transact([int, nval(lambda x: True, 'nothing'), GreaterThanConstraint(3)], 'c') == \
               [int, GreaterThanConstraint(3)]
        assert transact([int, GreaterThanConstraint(3), {'a': str, 'b': GreaterThanConstraint(2)}], 'a') == \
               [int, GreaterThanConstraint(3), str]
        assert transact([int, GreaterThanConstraint(3), {'a': str, 'b': GreaterThanConstraint(2)}], 'b') == \
               [int, GreaterThanConstraint(3)]
        assert transact([int, GreaterThanConstraint(3), {'a': str, 'b': GreaterThanConstraint(2)}], 'c') == \
               [int, GreaterThanConstraint(3)]
