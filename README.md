<div align="center">
    <a href="https://opendilab.github.io/treevalue/"><img width="1000px" height="auto" src="https://github.com/opendilab/treevalue/blob/main/docs/source/_static/title-banner.png"></a>
</div>

---

[![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Fopendilab)](https://twitter.com/opendilab)
[![PyPI](https://img.shields.io/pypi/v/treevalue)](https://pypi.org/project/treevalue/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/treevalue)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/ff0bc026423888cd7c4f287eaed4b3f5/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/ff0bc026423888cd7c4f287eaed4b3f5/raw/comments.json)

[![Docs Deploy](https://github.com/opendilab/treevalue/workflows/Docs%20Deploy/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Docs+Deploy%22)
[![Code Test](https://github.com/opendilab/treevalue/workflows/Code%20Test/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/opendilab/treevalue/workflows/Badge%20Creation/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Badge+Creation%22)
[![Package Release](https://github.com/opendilab/treevalue/workflows/Package%20Release/badge.svg)](https://github.com/opendilab/treevalue/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/opendilab/treevalue/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/opendilab/treevalue)

![GitHub Org's stars](https://img.shields.io/github/stars/opendilab)
[![GitHub stars](https://img.shields.io/github/stars/opendilab/treevalue)](https://github.com/opendilab/treevalue/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/opendilab/treevalue)](https://github.com/opendilab/treevalue/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/opendilab/treevalue)
[![GitHub issues](https://img.shields.io/github/issues/opendilab/treevalue)](https://github.com/opendilab/treevalue/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/opendilab/treevalue)](https://github.com/opendilab/treevalue/pulls)
[![Contributors](https://img.shields.io/github/contributors/opendilab/treevalue)](https://github.com/opendilab/treevalue/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/opendilab/treevalue)](https://github.com/opendilab/treevalue/blob/master/LICENSE)

`TreeValue` is a generalized tree-based data structure mainly developed by [OpenDILab Contributors](https://github.com/opendilab).

Almost all the operations can be supported in the form of trees in a convenient way to simplify the structure processing when the calculation is tree-based.

## Outline

* [Overview](#overview)
* [Getting Started](#getting-started)
    * [Prerequisite](#prerequisite)
    * [Installation](#installation)
    * [Quick Usage](#quick-usage)
    * [Tutorials](#tutorials)
    * [External](#external)
* [Speed Performance](#speed-performance)
* [Change Log](#change-log)
* [Feedback and Contribute](#feedback-and-contribute)
* [Citation](#citation)
* [License](#license)

## Overview

When we build a complex nested structure, we need to model it as a tree structure, and the native list and dict in Python are often used to solve this problem. However, it takes a lot of codes and some complex and non-intuitive calculation logic, which is not easy to modify and extend related code and data, and parallelization is impossible.

Therefore, we need a kind of more proper data container, named `TreeValue`. It is designed for solving the following problems:

- **Ease of Use**: When the existing operations are applied to tree structures such as dict, they will become completely unrecognizable, with really low readability and maintainability.
- **Diversity of Data**: In the tree structure operation, various abnormal conditions (structure mismatch, missing key-value, type mismatch, etc.) occur from time to time, and the code will be more complicated if it needs to be handled properly.
- **Scalability and Parallelization**: When any multivariate operation is performed, the calculation logic needs to be redesigned under the native Python code implementation, and the processing will be more complicated and confusing, and the code quality is difficult to control.

## Getting Started

### Prerequisite

`treevalue` has been fully tested in the Linux, macOS and Windows environments and with multiple Python versions, and it works properly on all these platforms.

However, **`treevalue` currently does not support PyPy**, so just pay attention to this when using it.

### Installation

You can simply install it with `pip` command line from the official PyPI site.

```shell
pip install treevalue
```

Or just from the source code on github

```shell
pip install git+https://github.com/opendilab/treevalue.git@main
```

For more information about installation, you can refer to the [installation guide](https://opendilab.github.io/treevalue/main/tutorials/installation/index.html).

After this, you can check if the installation is processed properly with the following code

```python
from treevalue import __version__
print('TreeValue version is', __version__)
```

### Quick Usage

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



### Tutorials

For more examples, explanations and further usages, take a look at:

* [Quick Start](https://opendilab.github.io/treevalue/main/tutorials/quick_start/index.html)
    * [Create a Simplest Tree](https://opendilab.github.io/treevalue/main/tutorials/quick_start/index.html#create-a-simplest-tree)
    * [Create a Slightly Complex Tree](https://opendilab.github.io/treevalue/main/tutorials/quick_start/index.html#create-a-slightly-complex-tree)
* [Basic Usage](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html)
    * [Create a Tree](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html#create-a-tree)
    * [Edit a Tree](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html#edit-the-tree)
    * [Do Index or Slice Calculation on The Tree](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html#do-index-or-slice-calculation-on-the-tree)
    * [Do Math Calculation on The Tree](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html#do-calculation-on-the-tree)
    * [Make Function Tree-Supported](https://opendilab.github.io/treevalue/main/tutorials/basic_usage/index.html#make-function-tree-supported)
* [Advanced Usage](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html)
    * [Function Modes](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#function-modes)
    * [Inheriting on Trees](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#inheriting-on-trees)
    * [Process Missing Values](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#process-missing-values)
    * [Functional Utilities](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#functional-utilities)
    * [Structural Utilities](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#structural-utilities)
    * [Tree Utilities](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#tree-utilities)
    * [Flatten Utilities](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#flatten-utilities)
    * [IO Utilities](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#io-utilities)
    * [Object Oriented Usage](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#object-oriented-usage)
    * [Costumize My TreeValue Class](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#diy-treevalue-class)
    * [Visualization of TreeValue](https://opendilab.github.io/treevalue/main/tutorials/advanced_usage/index.html#draw-graph-for-treevalue)

### External

We provide an official treevalue-based-wrapper for numpy and torch called [DI-treetensor](https://github.com/opendilab/DI-treetensor) since the `treevalue` is often used with libraries like `numpy` and `torch`. It will actually be helpful while working with AI fields.



## Speed Performance

Here is the speed performance of all the operations in `FastTreeValue`; the following table is the performance comparison result with [dm-tree](https://github.com/deepmind/tree).
(In DM-Tree, the `unflatten` operation is different from that in TreeValue, see: [Comparison Between TreeValue and DM-Tree](https://opendilab.github.io/treevalue/main/comparison/dmtree.result.html) for more details.)

|                                                     |     flatten      |  flatten(with path)   |        mapping        |     mapping(with path)      |
| --------------------------------------------------- | :--------------: | :-------------------: | :-------------------: | :-------------------------: |
| [treevalue](https://github.com/opendilab/treevalue) |       ---        | **511 ns ± 6.92 ns**  | **3.16 µs ± 42.8 ns** |     **1.58 µs ± 30 ns**     |
|                                                     |   **flatten**    | **flatten_with_path** |   **map_structure**   | **map_structure_with_path** |
| [dm-tree](https://github.com/deepmind/tree)         | 830 ns ± 8.53 ns |   11.9 µs ± 358 ns    |   13.3 µs ± 87.2 ns   |      62.9 µs ± 2.26 µs      |

The following 2 tables are the performance comparison result with [jax pytree](https://github.com/google/jax).

|                                                     |        mapping        |  mapping(with path)   |       flatten        |      unflatten       |    flatten_values    |     flatten_keys     |
| --------------------------------------------------- | :-------------------: | :-------------------: | :------------------: | :------------------: | :------------------: | :------------------: |
| [treevalue](https://github.com/opendilab/treevalue) | **2.21 µs ± 32.2 ns** | **2.16 µs ± 123 ns**  | **515 ns ± 7.53 ns** | **601 ns ± 5.99 ns** | **301 ns ± 12.9 ns** | **451 ns ± 17.3 ns** |
|                                                     |     **tree_map**      | **(Not Implemented)** |   **tree_flatten**   |  **tree_unflatten**  |   **tree_leaves**    |  **tree_structure**  |
| [jax pytree](https://github.com/google/jax)         |   4.67 µs ± 184 ns    |          ---          |  1.29 µs ± 27.2 ns   |   742 ns ± 5.82 ns   |   1.29 µs ± 22 ns    |  1.27 µs ± 16.5 ns   |

|                                                     |    flatten + all     |   flatten + reduce   | flatten + reduce(with init) | rise(given structure) | rise(automatic structure) |
| --------------------------------------------------- | :------------------: | :------------------: | :-------------------------: | :-------------------: | :-----------------------: |
| [treevalue](https://github.com/opendilab/treevalue) | **425 ns ± 9.33 ns** | **702 ns ± 5.93 ns** |    **793 ns ± 13.4 ns**     | **9.14 µs ± 129 ns**  |   **11.5 µs ± 182 ns**    |
|                                                     |     **tree_all**     |   **tree_reduce**    | **tree_reduce(with init)**  |  **tree_transpose**   |   **(Not Implemented)**   |
| [jax pytree](https://github.com/google/jax)         |   1.47 µs ± 37 ns    |  1.88 µs ± 27.2 ns   |      1.91 µs ± 47.4 ns      |    10 µs ± 117 ns     |            ---            |

This is the comparison between dm-tree, jax-libtree and us, with `flatten` and `mapping` operations (**lower value means less time cost and runs faster**)

![Time cost of flatten operation](docs/source/_static/Time%20cost%20of%20flatten%20operation.svg)

![Time cost of mapping operation](docs/source/_static/Time%20cost%20of%20mapping%20operation.svg)

The following table is the performance comparison result with [tianshou Batch](https://github.com/thu-ml/tianshou).

|                                                      |          get           |          set           |         init         |       deepcopy       |        stack         |          cat          |       split        |
| ---------------------------------------------------- | :--------------------: | :--------------------: | :------------------: | :------------------: | :------------------: | :-------------------: | :----------------: |
| [treevalue](https://github.com/opendilab/treevalue)  |   51.6 ns ± 0.609 ns   | **64.4 ns ± 0.564 ns** | **750 ns ± 14.2 ns** | **88.9 µs ± 887 ns** | **50.2 µs ± 771 ns** | **40.3 µs ± 1.08 µs** | **62 µs ± 1.2 µs** |
| [tianshou Batch](https://github.com/thu-ml/tianshou) | **43.2 ns ± 0.698 ns** |    396 ns ± 8.99 ns    |   11.1 µs ± 277 ns   |   89 µs ± 1.42 µs    |   119 µs ± 1.1 µs    |   194 µs ± 1.81 µs    |  653 µs ± 17.8 µs  |

And this is the comparison between Tianshou Batch and us, with `cat` , `stack` and `split` operations (**lower value means less time cost and runs faster**)

![Time cost of cat operation](docs/source/_static/Time%20cost%20of%20cat%20operation.svg)

![Time cost of stack operation](docs/source/_static/Time%20cost%20of%20stack%20operation.svg)

![Time cost of split operation](docs/source/_static/Time%20cost%20of%20split%20operation.svg)

Test benchmark code can be found here:

* [Comparison with dm-tree](https://github.com/opendilab/treevalue/blob/main/test/compare/deepmind/test_dm_tree.py)
* [Comparison with jax-libtree](https://github.com/opendilab/treevalue/blob/main/test/compare/jax/test_jax.py)
* [Comparison with tianshou Batch](https://github.com/opendilab/treevalue/blob/main/test/compare/tianshou/test_tianshou_batch.py)

## Change Log

<details><summary><b>Version History</b> <i>[click to expand]</i></summary>
<div>

* 2022-05-03
        1.3.1: Change definition of getitem, setitem and delitem; add pop method for TreeValue class.
* 2022-03-15
        1.3.0: Add getitem, setitem and delitem for adding, editing and removing items in TreeValue class.
* 2022-02-22
  	1.2.2: Optimize union function; add walk utility method.
* 2022-01-26
        1.2.1: Update tree printing; add keys, values, items on TreeValue; add comparision to facebook nest library.
* 2022-01-04
        1.2.0: Add flatten_values and flatten_keys; fix problem in mapping function; add support for potc.
* 2021-12-03
        1.1.0: Add version information; fix bug of default value; add flatten and unflatten; optimization speed performance.
* 2021-10-24
        1.0.0: Greatly optimize the speed performance using cython, overhead has been reduced to a negligible level.
    </div>
    </details>

## Feedback and Contribute

Welcome to **OpenDILab** community - treevalue!

If you meet some problem or have some brilliant ideas, you can [file an issue](https://github.com/opendilab/treevalue/issues/new/choose).

<b>Scan the QR code and add us on Wechat:</b>

<div align="center">
<img src='https://github.com/opendilab/DI-engine/raw/main/assets/wechat.png' width="25%" />
</div>

Or just contact us with [slack](https://opendilab.slack.com/join/shared_invite/zt-v9tmv4fp-nUBAQEH1_Kuyu_q4plBssQ#/shared-invite/email) or email (opendilab.contact@gmail.com).

Please check [Contributing Guidances](https://github.com/opendilab/treevalue/blob/main/CONTRIBUTING.md).

Thanks to the following contributors! 

<a href="https://github.com/opendilab/treevalue/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=opendilab/treevalue" />
</a>

## Citation

```
@misc{treevalue,
    title={{TreeValue} - Tree-Structure Computing Solution},
    author={TreeValue Contributors},
    publisher = {GitHub},
    howpublished = {\url{https://github.com/opendilab/treevalue}},
    year={2021},
}
```

## License

`treevalue` released under the Apache 2.0 license. See the [LICENSE](./LICENSE) file for details.
