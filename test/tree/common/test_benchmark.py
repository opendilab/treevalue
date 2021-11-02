from operator import __eq__

import pytest

from treevalue.tree.common import create_storage, raw, TreeStorage, unraw

_TREE_RAW_DATA = {'a': 1, 'b': 2, 'c': raw({'x': 3, 'y': 4}), 'd': {'x': 3, 'y': 4}}
_TREE_STORAGE = create_storage(_TREE_RAW_DATA)
_TREE_DATA = _TREE_STORAGE.detach()

_TREE_RAW_DATA_2 = {'e': 3, 'f': 'klsjdfgklsdf', 'g': raw({'x': 3, 'y': 4}), 'c': {'x': 3, 'y': 4}}
_TREE_STORAGE_2 = create_storage(_TREE_RAW_DATA_2)
_TREE_DATA_2 = _TREE_STORAGE_2.detach()


@pytest.mark.benchmark(group='tree_storage')
class TestTreeStorageBenchmark:
    def setup(self):
        self.st = create_storage(_TREE_RAW_DATA)

    @pytest.mark.parametrize('data', [1, {'x': 3, 'y': 4}])
    def test_raw(self, benchmark, data):
        result = benchmark(raw, data)
        assert unraw(result) is data

    @pytest.mark.parametrize('data', [_TREE_RAW_DATA])
    def test_create_storage(self, benchmark, data):
        result = benchmark(create_storage, data)
        assert result == _TREE_STORAGE

    @pytest.mark.parametrize('data', [_TREE_DATA])
    def test_init_storage(self, benchmark, data):
        result = benchmark(TreeStorage, data)
        assert result == _TREE_STORAGE

    def __setup_storage(self):
        return create_storage(_TREE_RAW_DATA)

    @pytest.mark.parametrize('key', ['a'])
    def test_get(self, benchmark, key):
        benchmark(TreeStorage.get, self.__setup_storage(), key)

    @pytest.mark.parametrize('key, data', [('b', {'x': 1, 'y': 2})])
    def test_set(self, benchmark, key, data):
        benchmark(TreeStorage.set, self.__setup_storage(), key, data)

    @pytest.mark.parametrize('key', ['a'])
    def test_del_after_set(self, benchmark, key):
        def set_and_del(st: TreeStorage, k: str):
            st.set(k, 1)
            st.del_(k)

        benchmark(set_and_del, self.__setup_storage(), key)

    @pytest.mark.parametrize('key', ['a'])
    def test_contains(self, benchmark, key):
        benchmark(TreeStorage.contains, self.__setup_storage(), key)

    def test_size(self, benchmark):
        benchmark(TreeStorage.size, self.__setup_storage())

    def test_empty(self, benchmark):
        benchmark(TreeStorage.empty, self.__setup_storage())

    def test_detach(self, benchmark):
        benchmark(TreeStorage.detach, self.__setup_storage())

    def test_dump(self, benchmark):
        benchmark(TreeStorage.dump, self.__setup_storage())

    def test_deepdump(self, benchmark):
        benchmark(TreeStorage.deepdump, self.__setup_storage())

    def test_copy(self, benchmark):
        benchmark(TreeStorage.copy, self.__setup_storage())

    def test_deepcopy(self, benchmark):
        benchmark(TreeStorage.deepcopy, self.__setup_storage())

    @pytest.mark.parametrize('st', [_TREE_STORAGE_2])
    def test_copy_from(self, benchmark, st):
        benchmark(TreeStorage.copy_from, self.__setup_storage(), st)

    @pytest.mark.parametrize('st', [_TREE_STORAGE_2])
    def test_deepcopy_from(self, benchmark, st):
        benchmark(TreeStorage.deepcopy_from, self.__setup_storage(), st)

    def test_repr(self, benchmark):
        benchmark(repr, self.__setup_storage())

    def test_eq(self, benchmark):
        benchmark(__eq__, _TREE_STORAGE, _TREE_STORAGE_2)
