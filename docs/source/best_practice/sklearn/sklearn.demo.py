import numpy as np
from sklearn.decomposition import PCA

from treevalue import FastTreeValue

fit_transform = FastTreeValue.func()(lambda x: PCA(min(*x.shape)).fit_transform(x))

if __name__ == '__main__':
    data = FastTreeValue({
        'a': np.random.randint(-5, 15, (4, 3)),
        'x': {
            'c': np.random.randint(-15, 5, (5, 4)),
        }
    })
    print("Original int data:")
    print(data)

    pdata = fit_transform(data)
    print("Fit transformed data:")
    print(pdata)
