Advanced Usage
===================

In this part, Some of the advanced usages of `TreeValue` \
will be introduced one by one with sample code and \
graph to explain them.

For further information or usage of `TreeValue` and `FastTreeValue`, \
you may take a look at the following pages:

* `TreeValue` and its utilities: :doc:`../../api_doc/tree/tree`.
* `func_treelize` and other wrappers: :doc:`../../api_doc/tree/func`.
* `FastTreeValue` and its operators, methods: :doc:`../../api_doc/tree/general`.

Function modes
-------------------------

In the basic usage description in :ref:`tutorials_basicusage_func`, \
we can see that a common function which only support the calculation \
of the common values can be wrapped to support the tree-based \
calculation painlessly.

Here is the documentation of function `treevalue.tree.func.func_treelize`.

.. autofunction:: treevalue.tree.func.func_treelize
    :noindex:

In the arguments listed above, 3 of them are key arguments:

* **mode**, Tree process mode of the calculation. Will be introduced in this section.
* **inherit**, Inheriting mode of the calculation on the tree. Will be introduced in :ref:`tutorials_advancedusage_inherit`.
* **missing**, Missing processor of the calculation on the tree. Will be introduced in :ref:`tutorials_advancedusage_missing`.

The mode argument is the most important argument in function `func_treelize`. \
For it depends the basic logic of the graph calculation.

The type of `mode` argument is `TreeMode`, which documentation is like this.

.. autoenum:: treevalue.tree.func.TreeMode
    :noindex:

In this part, all of the 4 modes will be introduced \
with details and samples one by one.

Strict Mode
~~~~~~~~~~~~~~~~~

Strict mode is the most frequently-used mode in real cases. \
It is also the default value of the `mode` argument in the \
treelize functions.

To be simple, strict mode need the keys of a node in the tree \
be strictly mapped one by one, missing or overage of the keys \
are both forbidden in strict mode, which means `KeyError` will \
be raised.

For example, In the trees in `strict_demo_1`, \
if we need to added `t1` and `t2` together, `t3` will be the result. \
Because all the keys (`a`, `b`, `x` of the root nodes, \
and `c`, `d`, `e` of the `x` node) can be mapped one by one.

.. image:: strict_demo_1.gv.svg
    :align: center

In another situation, when the keys are not so regular like \
that in `strict_demo_1`, like the trees in `strict_demo_2`. \
If we try to add `t1` and `t2` in strict mode, `KeyError` will \
be raised due to the missing of key `a` in `t1` and key `f` in `t2.x`.

.. image:: strict_demo_2.gv.svg
    :align: center

Here is a real code example of strict mode.

.. todo:: write a code example here


Left Mode
~~~~~~~~~~~~~~~~

.. todo:: describe left mode and samples


Inner Mode
~~~~~~~~~~~~~~~~~~~~

.. todo:: describe inner mode and samples


Outer Mode
~~~~~~~~~~~~~~~~~~~

.. todo:: describe outer mode and samples



.. _tutorials_advancedusage_inherit:

Inherit mode
-------------------

.. todo:: introduce how this framework process inherited values


.. _tutorials_advancedusage_missing:

Process missing values
--------------------------

.. todo:: introduce how this framework process key missing situation


Functional utilities
-----------------------

.. todo:: writing mapping, filter, mask, shrink here

Structural utilities
--------------------

.. todo:: writing union, subside, rise here

Tree utilities
------------------

.. todo:: writing jsonify, view, clone, typetrans here

Decorators
--------------

.. todo:: writing func_treelize, method_treelize and classmethod_treelize, \
    method_treelize is also supported to property getter.

DIY new treevalue class
-----------------------------

.. todo:: introduce general_treelize here, especially how to support add.

Other
--------------------



