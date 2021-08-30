import os
import tempfile

from treevalue import TreeValue, dump, load

if __name__ == '__main__':
    t = TreeValue({'a': 'ab', 'b': 'Cd', 'x': {'c': 'eF', 'd': 'GH'}})
    print('t:', t, sep=os.linesep)

    with tempfile.NamedTemporaryFile() as tf:
        with open(tf.name, 'wb') as wf:  # dump t to file
            dump(t, file=wf)

        with open(tf.name, 'rb') as rf:  # load dt from file
            dt = load(file=rf)

    assert dt == t
    print('dt:', dt, sep=os.linesep)
