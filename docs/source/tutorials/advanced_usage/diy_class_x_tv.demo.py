import pathlib
import sys

from treevalue import FastTreeValue

if __name__ == '__main__':
    _module = sys.modules[FastTreeValue.__module__]
    print(pathlib.Path(_module.__file__).read_text())
