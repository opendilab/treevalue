import zlib

import pytest

from treevalue.tree import loads, dumps, FastTreeValue


class MyTreeValue(FastTreeValue):
    pass


@pytest.mark.unittest
class TestTreeTreeIo:
    def test_dumps_and_loads(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        t1 = loads(dumps(t), type_=FastTreeValue)
        assert len(dumps(t)) < 130
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        t2 = loads(dumps(t), type_=MyTreeValue)
        assert isinstance(t2, MyTreeValue)
        assert t2 != t
        assert FastTreeValue(t2) == t

    def test_dumps_and_loads_with_zip(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})

        t1 = loads(dumps(t, compress=zlib.compress), type_=FastTreeValue, decompress=zlib.decompress)
        assert len(dumps(t, compress=zlib.compress)) < 105
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        t2 = loads(dumps(t, compress=zlib.compress), type_=MyTreeValue, decompress=zlib.decompress)
        assert isinstance(t2, MyTreeValue)
        assert t2 != t
        assert FastTreeValue(t2) == t
