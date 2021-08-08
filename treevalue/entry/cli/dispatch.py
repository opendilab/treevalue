from .base import _base_treevalue_cli
from .graph import _graph_cli
from .utils import _build_cli

treevalue_cli = _build_cli(_base_treevalue_cli, _graph_cli)
