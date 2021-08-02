import json

from treevalue import TreeValue, raw, jsonify

if __name__ == '__main__':
    t = TreeValue({'a': 1, 'b': [2, 3], 'x': {'c': raw({'x': 1, 'y': 2}), 'd': "this is a string"}})

    print("Tree t:")
    print(t)

    print("Json data of t:")
    print(json.dumps(jsonify(t), indent=4, sort_keys=True))
