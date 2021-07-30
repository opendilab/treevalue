import numpy as np

T, B = 3, 4


def without_treevalue(batch_):
    mean_b_list = []
    even_index_a_list = []
    for i in range(len(batch_)):
        for k, v in batch_[i].items():
            if k == 'a':
                v = v.astype(np.float32)
                even_index_a_list.append(v[::2])
            elif k == 'b':
                v = v.astype(np.float32)
                transformed_v = np.power(v, 2) + 1.0
                mean_b_list.append(transformed_v.mean())
            elif k == 'c':
                for k1, v1 in v.items():
                    if k1 == 'd':
                        v1 = v1.astype(np.float32)
                    else:
                        print('ignore keys: {}'.format(k1))
            else:
                print('ignore keys: {}'.format(k))
    for i in range(len(batch_)):
        for k in batch_[i].keys():
            if k == 'd':
                batch_[i][k]['noise'] = np.random.random(size=(3, 4, 5))

    mean_b = sum(mean_b_list) / len(mean_b_list)
    even_index_a = np.stack(even_index_a_list, axis=0)
    return batch_, mean_b, even_index_a
