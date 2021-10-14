import zlib

import pytest

from treevalue.tree import loads, dumps, FastTreeValue


class MyTreeValue(FastTreeValue):
    pass


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestTreeTreeIo:
    def test_dumps_and_loads(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': [3] * 1000, 'd': 4}})

        _dumped_data = dumps(t)
        t1 = loads(_dumped_data, type_=FastTreeValue)
        assert 2130 < len(_dumped_data) < 2170
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        t2 = loads(_dumped_data, type_=MyTreeValue)
        assert isinstance(t2, MyTreeValue)
        assert t2 != t
        assert FastTreeValue(t2) == t

        with pytest.warns(UserWarning):
            t1 = loads(_dumped_data, decompress=zlib.decompress, type_=FastTreeValue)
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

    def test_dumps_and_loads_with_zip(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': [3] * 1000, 'd': 4}})

        _dumped_data = dumps(t, compress=zlib)
        t1 = loads(_dumped_data, type_=FastTreeValue)
        assert 210 < len(dumps(t, compress=zlib)) < 230
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        t2 = loads(_dumped_data, type_=MyTreeValue)
        assert isinstance(t2, MyTreeValue)
        assert t2 != t
        assert FastTreeValue(t2) == t

        with pytest.warns(UserWarning):
            t1 = loads(_dumped_data, decompress=zlib.decompress, type_=FastTreeValue)
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

    def test_dumps_and_loads_with_zip_tuple(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': [3] * 1000, 'd': 4}})

        _dumped_data = dumps(t, compress=(zlib.compress, zlib.decompress))
        t1 = loads(_dumped_data, type_=FastTreeValue)
        assert 210 < len(_dumped_data) < 230
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        t2 = loads(_dumped_data, type_=MyTreeValue)
        assert isinstance(t2, MyTreeValue)
        assert t2 != t
        assert FastTreeValue(t2) == t

    def test_dumps_and_loads_with_compress_only(self):
        t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': [3] * 1000, 'd': 4}})

        _dumped_data = dumps(t, compress=zlib.compress)
        t1 = loads(_dumped_data, decompress=zlib.decompress, type_=FastTreeValue)
        assert 130 < len(_dumped_data) < 150
        assert isinstance(t1, FastTreeValue)
        assert t1 == t

        with pytest.raises(RuntimeError):
            loads(_dumped_data, type_=FastTreeValue)
