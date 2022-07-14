import pytest
from .base import get_fasttreevalue_test
from treevalue.tree import FastTreeValue



class _MyMetaClass(type):
    pass


class MyMetaTreeValue(FastTreeValue, metaclass=_MyMetaClass):
    pass


@pytest.mark.unittest
class TestTreeGeneralMeta(get_fasttreevalue_test(MyMetaTreeValue)):
    pass
