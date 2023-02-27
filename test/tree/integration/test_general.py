from collections import namedtuple
from dataclasses import dataclass

import pytest
from easydict import EasyDict

from treevalue import generic_flatten, generic_unflatten, FastTreeValue, register_integrate_container


@dataclass
class DC:
    x: int
    y: str


nt = namedtuple('nt', ['a', 'b'])


class MyTreeValue(FastTreeValue):
    pass


@pytest.mark.unittest
class TestTreeIntegrationGeneral:
    def test_general_flatten_and_unflatten(self):
        demo_data = {
            'a': 1,
            'b': [2, 3, 'f'],
            'c': (2, 5, 'ds', EasyDict({
                'x': None,
                'z': DC(34, '1.2'),
            })),
            'd': nt('f', 100),
            'e': MyTreeValue({'x': 1, 'y': 'dsfljk'})
        }
        v, spec = generic_flatten(demo_data)
        assert v == [1, [2, 3, 'f'], [2, 5, 'ds', [None, [34, '1.2']]], ['f', 100], [1, 'dsfljk']]

        rv = generic_unflatten(v, spec)
        assert rv == demo_data
        assert isinstance(rv['c'][-1], EasyDict)
        assert isinstance(rv['d'], nt)
        assert isinstance(rv['c'][-1]['z'], DC)
        assert isinstance(rv['e'], MyTreeValue)

    def test_register_my_class(self):
        class MyDC:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __eq__(self, other):
                return isinstance(other, MyDC) and self.x == other.x and self.y == other.y

        def _mydc_flatten(v):
            return [v.x, v.y], MyDC

        def _mydc_unflatten(v, spec):
            return spec(*v)

        register_integrate_container(MyDC, _mydc_flatten, _mydc_unflatten)

        demo_data = {
            'a': 1,
            'b': [2, 3, 'f'],
            'c': (2, 5, 'ds', EasyDict({
                'x': None,
                'z': MyDC(34, '1.2'),
            })),
            'd': nt('f', 100),
            'e': MyTreeValue({'x': 1, 'y': 'dsfljk'})
        }
        v, spec = generic_flatten(demo_data)
        assert v == [1, [2, 3, 'f'], [2, 5, 'ds', [None, [34, '1.2']]], ['f', 100], [1, 'dsfljk']]

        rv = generic_unflatten(v, spec)
        assert rv == demo_data
        assert isinstance(rv['c'][-1], EasyDict)
        assert isinstance(rv['d'], nt)
        assert isinstance(rv['c'][-1]['z'], MyDC)
        assert isinstance(rv['e'], MyTreeValue)
