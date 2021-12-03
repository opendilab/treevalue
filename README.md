# treevalue

[![PyPI](https://img.shields.io/pypi/v/treevalue)](https://pypi.org/project/treevalue/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/treevalue)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/ff0bc026423888cd7c4f287eaed4b3f5/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/ff0bc026423888cd7c4f287eaed4b3f5/raw/comments.json)


[![Docs Deploy](https://github.com/opendilab/treevalue/workflows/Docs%20Deploy/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Docs+Deploy%22)
[![Code Test](https://github.com/opendilab/treevalue/workflows/Code%20Test/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/opendilab/treevalue/workflows/Badge%20Creation/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Badge+Creation%22)
[![Package Release](https://github.com/opendilab/treevalue/workflows/Package%20Release/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/opendilab/treevalue/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/opendilab/treevalue)

[![GitHub stars](https://img.shields.io/github/stars/opendilab/treevalue)](https://github.com/opendilab/treevalue/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/opendilab/treevalue)](https://github.com/opendilab/treevalue/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/opendilab/treevalue)
[![GitHub issues](https://img.shields.io/github/issues/opendilab/treevalue)](https://github.com/opendilab/treevalue/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/opendilab/treevalue)](https://github.com/opendilab/treevalue/pulls)
[![Contributors](https://img.shields.io/github/contributors/opendilab/treevalue)](https://github.com/opendilab/treevalue/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/opendilab/treevalue)](https://github.com/opendilab/treevalue/blob/master/LICENSE)

`TreeValue` is a generalized tree-based data structure mainly developed by [OpenDILab Contributors](https://github.com/opendilab).

Almost all the operation can be supported in form of trees in a convenient way to simplify the structure processing when the calculation is tree-based.

## Installation

You can simply install it with `pip` command line from the official PyPI site.

```shell
pip install treevalue
```

For more information about installation, you can refer to [Installation](https://opendilab.github.io/treevalue/main/tutorials/installation/index.html#).

## Documentation

The detailed documentation are hosted on [https://opendilab.github.io/treevalue](https://opendilab.github.io/treevalue/).

Only english version is provided now, the chinese documentation is still under development.

## Quick Start

You can easily create a tree value object based on `FastTreeValue`.

```python
from treevalue import FastTreeValue

if __name__ == '__main__':
    t = FastTreeValue({
        'a': 1,
        'b': 2.3,
        'x': {
            'c': 'str',
            'd': [1, 2, None],
            'e': b'bytes',
        }
    })
    print(t)

```

The result should be

```text
<FastTreeValue 0x7f6c7df00160 keys: ['a', 'b', 'x']>
├── 'a' --> 1
├── 'b' --> 2.3
└── 'x' --> <FastTreeValue 0x7f6c81150860 keys: ['c', 'd', 'e']>
    ├── 'c' --> 'str'
    ├── 'd' --> [1, 2, None]
    └── 'e' --> b'bytes'
```

And `t` is structure should be like this

![](https://opendilab.github.io/treevalue/main/_images/simple_demo.dat.svg)

Not only a visible tree structure, but abundant operation supports is provided. 
You can just put objects (such as `torch.Tensor`, or any other types) here and just 
call their methods, like this

```python
import torch

from treevalue import FastTreeValue

t = FastTreeValue({
    'a': torch.rand(2, 5),
    'x': {
        'c': torch.rand(3, 4),
    }
})

print(t)
# <FastTreeValue 0x7f8c069346a0>
# ├── a --> tensor([[0.3606, 0.2583, 0.3843, 0.8611, 0.5130],
# │                 [0.0717, 0.1370, 0.1724, 0.7627, 0.7871]])
# └── x --> <FastTreeValue 0x7f8ba6130f40>
#     └── c --> tensor([[0.2320, 0.6050, 0.6844, 0.3609],
#                       [0.0084, 0.0816, 0.8740, 0.3773],
#                       [0.6523, 0.4417, 0.6413, 0.8965]])

print(t.shape)  # property access
# <FastTreeValue 0x7f8c06934ac0>
# ├── a --> torch.Size([2, 5])
# └── x --> <FastTreeValue 0x7f8c069346d0>
#     └── c --> torch.Size([3, 4])
print(t.sin())  # method call
# <FastTreeValue 0x7f8c06934b80>
# ├── a --> tensor([[0.3528, 0.2555, 0.3749, 0.7586, 0.4908],
# │                 [0.0716, 0.1365, 0.1715, 0.6909, 0.7083]])
# └── x --> <FastTreeValue 0x7f8c06934b20>
#     └── c --> tensor([[0.2300, 0.5688, 0.6322, 0.3531],
#                       [0.0084, 0.0816, 0.7669, 0.3684],
#                       [0.6070, 0.4275, 0.5982, 0.7812]])
print(t.reshape((2, -1)))  # method with arguments
# <FastTreeValue 0x7f8c06934b80>
# ├── a --> tensor([[0.3606, 0.2583, 0.3843, 0.8611, 0.5130],
# │                 [0.0717, 0.1370, 0.1724, 0.7627, 0.7871]])
# └── x --> <FastTreeValue 0x7f8c06934b20>
#     └── c --> tensor([[0.2320, 0.6050, 0.6844, 0.3609, 0.0084, 0.0816],
#                       [0.8740, 0.3773, 0.6523, 0.4417, 0.6413, 0.8965]])
print(t[:, 1:-1])  # index operator
# <FastTreeValue 0x7f8ba5c8eca0>
# ├── a --> tensor([[0.2583, 0.3843, 0.8611],
# │                 [0.1370, 0.1724, 0.7627]])
# └── x --> <FastTreeValue 0x7f8ba5c8ebe0>
#     └── c --> tensor([[0.6050, 0.6844],
#                       [0.0816, 0.8740],
#                       [0.4417, 0.6413]])
print(1 + (t - 0.8) ** 2 * 1.5)  # math operators
# <FastTreeValue 0x7fdfa5836b80>
# ├── a --> tensor([[1.6076, 1.0048, 1.0541, 1.3524, 1.0015],
# │                 [1.0413, 1.8352, 1.2328, 1.7904, 1.0088]])
# └── x --> <FastTreeValue 0x7fdfa5836880>
#     └── c --> tensor([[1.1550, 1.0963, 1.3555, 1.2030],
#                       [1.0575, 1.4045, 1.0041, 1.0638],
#                       [1.0782, 1.0037, 1.5075, 1.0658]])
```

For more quick start explanation and further usage, take a look at:

* [Quick Start](https://opendilab.github.io/treevalue/main/tutorials/quick_start/index.html)
* [Basic Usage](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html)
* [Advanced Usage](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html)

## Speed Performance

Here is the speed performance of all the operations in `FastTreeValue`

|                                                     |     flatten      |  flatten(with path)  |          map          |   map(with path)    |
| --------------------------------------------------- | :--------------: | :------------------: | :-------------------: | :-----------------: |
| [treevalue](https://github.com/opendilab/treevalue) |       ---        | **511 ns ± 6.92 ns** | **3.16 µs ± 42.8 ns** | **1.58 µs ± 30 ns** |
| [dm-tree](https://github.com/deepmind/tree)         | 830 ns ± 8.53 ns |   11.9 µs ± 358 ns   |   13.3 µs ± 87.2 ns   |  62.9 µs ± 2.26 µs  |



|                                                      |          get           |          set           |         init         |       deepcopy       |        stack         |          cat          |       split        |
| ---------------------------------------------------- | :--------------------: | :--------------------: | :------------------: | :------------------: | :------------------: | :-------------------: | :----------------: |
| [treevalue](https://github.com/opendilab/treevalue)  |   51.6 ns ± 0.609 ns   | **64.4 ns ± 0.564 ns** | **750 ns ± 14.2 ns** | **88.9 µs ± 887 ns** | **50.2 µs ± 771 ns** | **40.3 µs ± 1.08 µs** | **62 µs ± 1.2 µs** |
| [tianshou Batch](https://github.com/thu-ml/tianshou) | **43.2 ns ± 0.698 ns** |    396 ns ± 8.99 ns    |   11.1 µs ± 277 ns   |   89 µs ± 1.42 µs    |   119 µs ± 1.1 µs    |   194 µs ± 1.81 µs    |  653 µs ± 17.8 µs  |

And this is the comparasion between tianshou Batch and us, with `cat` , `stack` and `split` operations

![Time cost of cat operation](docs/source/_static/Time%20cost%20of%20cat%20operation.png)

![Time cost of stack operation](docs/source/_static/Time%20cost%20of%20stack%20operation.png)

![Time cost of split operation](docs/source/_static/Time%20cost%20of%20split%20operation.png)

Test benchmark code can be found here:

* [Comparasion with dm-tree](https://github.com/opendilab/treevalue/blob/main/test/compare/test_dm_tree.py)
* [Comparasion with tianshou Batch](https://github.com/opendilab/treevalue/blob/main/test/compare/test_tianshou_batch.py)


## Contribution

We appreciate all contributions to improve treevalue, both logic and system designs. Please refer to CONTRIBUTING.md for more guides.

And users can join our [slack communication channel](https://join.slack.com/t/opendilab/shared_invite/zt-v9tmv4fp-nUBAQEH1_Kuyu_q4plBssQ), or contact the core developer [HansBug](https://github.com/HansBug) for more detailed discussion.

## License

`treevalue` released under the Apache 2.0 license.
