import numpy as np

from treevalue import FastTreeValue

T, B = 3, 4
power = FastTreeValue.func()(np.power)
stack = FastTreeValue.func(subside=True)(np.stack)
split = FastTreeValue.func(rise=True)(np.split)


def with_treevalue(batch_):
    batch_ = [FastTreeValue(b) for b in batch_]
    batch_ = stack(batch_)
    batch_ = batch_.astype(np.float32)
    batch_.b = power(batch_.b, 2) + 1.0
    batch_.c.noise = np.random.random(size=(B, 3, 4, 5))
    mean_b = batch_.b.mean()
    even_index_a = batch_.a[:, ::2]
    batch_ = split(batch_, indices_or_sections=B, axis=0)
    return batch_, mean_b, even_index_a
