import numpy as np

from treevalue import reduce_, FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({
        'a': np.identity(3),
        'b': np.array([[1, 2], [3, 4]]),
        'x': {
            'c': np.zeros(4),
            'd': np.array([[5, 6, 7], [8, 9, 10]])
        },
    })

    print("Size tree:", t.nbytes)
    print("Total bytes of arrays in t:",
          reduce_(t.nbytes, lambda **kwargs: sum(kwargs.values())))
