import numpy as np

from treevalue import FastTreeValue, func_treelize

T, B = 3, 4
power = func_treelize()(np.power)
stack = func_treelize(subside=True)(np.stack)
split = func_treelize(rise=True)(np.split)


@func_treelize()
def astype(item, *args):
    return item.astype(*args)


def with_treevalue(batch_):
    batch_ = [FastTreeValue(b) for b in batch_]
    batch_ = stack(batch_)
    batch_ = astype(batch_, np.float32)
    batch_.b = power(batch_.b, 2) + 1.0
    batch_.c.noise = np.random.random(size=(B, 3, 4, 5))
    mean_b = batch_.b.mean()
    even_index_a = batch_.a[:, ::2]
    batch_ = split(batch_, indices_or_sections=B, axis=0)
    return batch_, mean_b, even_index_a
