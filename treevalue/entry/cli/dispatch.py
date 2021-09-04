from .base import _base_treevalue_cli
from .export import _export_cli
from .graph import _graph_cli
from .utils import _cli_builder

treevalue_cli = _cli_builder(
    _base_treevalue_cli,
    _graph_cli,  # treevalue graph
    _export_cli,  # treevalue export
)
