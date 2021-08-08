import pytest

from treevalue.utils import import_object, quick_import_object, import_all

OBJ = 1
P_1 = 2
P_2 = 3
P_3 = 4


@pytest.mark.unittest
class TestUtilsImports:
    def test_import_object(self):
        assert import_object('OBJ', 'test.utils.test_imports') == 1
        assert import_object('zip') == zip

    def test_quick_import_object(self):
        assert quick_import_object('test.utils.test_imports.OBJ') == 1
        assert quick_import_object('zip') == zip
        assert quick_import_object('zip.__dict__') == zip.__dict__

        with pytest.raises(AttributeError):
            quick_import_object('p233')
        with pytest.raises(ModuleNotFoundError):
            quick_import_object('zip.no_such_attr')

    def test_import_all(self):
        assert import_all('test.utils.test_imports',
                          predicate=lambda k, v: k.startswith('P_')) == {
                   'P_1': P_1, 'P_2': P_2, 'P_3': P_3,
               }
        assert {k: v for k, v in import_all('test.utils.test_imports').items() if
                k in {'P_1', 'P_2', 'P_3', 'OBJ'}} == {
                   'P_1': P_1, 'P_2': P_2, 'P_3': P_3, 'OBJ': 1,
               }
