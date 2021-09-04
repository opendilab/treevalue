import numpy as np

from treevalue import FastTreeValue

st1 = FastTreeValue({
    'a': 1,
    'b': [1, 2],
    'x': {
        'c': 3,
        'd': np.zeros((3, 2)),
    }
})
st2 = FastTreeValue({
    'np': st1.x.d,
    'ar': st1.b,
    'a': st1.a,
    'arx': [1, 2],
})
