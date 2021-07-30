from treevalue.utils import build_graph

if __name__ == '__main__':
    t1 = {'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}}
    t2 = {'f': 4, 'y': t1['x'], 'z': {'e': [5, 7], 'f': "string"}}
    g = build_graph((t1, 't1'), (t2, 't2'), graph_title="Complex demo of build_graph.")

    print(g.source)
    print(g.save('build_graph_complex_demo.dat.gv'))
    print(g.render(format='svg'))
