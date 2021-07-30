import copy

import numpy as np
from with_treevalue import with_treevalue
from without_treevalue import without_treevalue

T, B = 3, 4


def get_data():
    return {
        'a': np.random.random(size=(T, 8)),
        'b': np.random.random(size=(6,)),
        'c': {
            'd': np.random.randint(0, 10, size=(1,))
        }
    }


if __name__ == "__main__":
    batch = [get_data() for _ in range(B)]
    batch0, mean0, even_index_a0 = without_treevalue(copy.deepcopy(batch))
    batch1, mean1, even_index_a1 = with_treevalue(copy.deepcopy(batch))

    assert np.abs(mean0 - mean1) < 1e-6
    print('mean0 & mean1:', mean0, mean1)

    assert np.abs((even_index_a0 - even_index_a1).max()) < 1e-6
    print('even_index_a0:', even_index_a0)
    print('even_index_a1:', even_index_a1)

    assert len(batch0) == B
    assert len(batch1) == B
