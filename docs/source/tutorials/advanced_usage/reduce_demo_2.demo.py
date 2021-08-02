from treevalue import reduce_, FastTreeValue, mapping

if __name__ == '__main__':
    t = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}, 'y': {'e': 6, 'f': 8}})

    weights = mapping(t, lambda v, p: v * len(p))
    print("Weight tree:", weights)
    print("Huffman weight sum of t:", reduce_(weights, lambda **kwargs: sum(kwargs.values())))
