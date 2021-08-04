from treevalue.utils import build_graph

if __name__ == '__main__':
    t = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    g = build_graph((t, 't'), graph_title="Demo of build_graph.")

    print(g.source)
    print(g.render('build_graph_demo.dat.gv', format='svg'))
