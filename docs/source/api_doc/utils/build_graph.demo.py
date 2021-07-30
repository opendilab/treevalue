import os

from treevalue.utils import build_graph

if __name__ == '__main__':
    t = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    g = build_graph((t, 't'))

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(g.source)
    print(g.save('build_graph_demo.dat.gv'))
    print(g.render(format='svg'))
