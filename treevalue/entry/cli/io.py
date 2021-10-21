import glob
import os
import pickle
from string import Template
from typing import Tuple, Iterator

import dill
from hbutils.reflection import dynamic_call, iter_import_objects

from ...tree import TreeValue, load


@dynamic_call
def _import_trees_from_package(obj_pattern, title=None, *args,
                               default_template: str = '$name') -> Iterator[Tuple[TreeValue, str]]:
    _title_template = Template(title or default_template)
    for _object, _module, _name in iter_import_objects(obj_pattern, lambda o: isinstance(o, TreeValue)):
        _title = _title_template.safe_substitute(dict(module=_module, name=_name))
        yield _object, _title


@dynamic_call
def _import_trees_from_binary(filename_pattern, title='', *args,
                              default_template: str = '$bodyname') -> Iterator[Tuple[TreeValue, str]]:
    _title_template = Template(title or default_template)
    for filename in glob.glob(filename_pattern):
        if not os.path.exists(filename) or not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            continue

        filename = os.path.abspath(filename)
        _name_body, _name_ext = os.path.splitext(os.path.basename(filename))
        _name_ext = _name_ext[1:] if _name_ext.startswith('.') else _name_ext
        with open(filename, 'rb') as file:
            try:
                _tree = load(file)
            except (pickle.UnpicklingError, dill.UnpicklingError, EOFError, IOError):
                continue
            else:
                yield _tree, _title_template.safe_substitute(dict(
                    fullname=filename,
                    dirname=os.path.dirname(filename),
                    basename=os.path.basename(filename),
                    extname=_name_ext,
                    bodyname=_name_body,
                ))
