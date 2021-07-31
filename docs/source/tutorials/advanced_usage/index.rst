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
~~~~~~~~~~~~~~~~~~~~~~~~~

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


.. todo:: introduce strict, left, inner, outer mode and their differences


.. _tutorials_advancedusage_inherit:

Inherit mode
~~~~~~~~~~~~~~~~~~~

.. todo:: introduce how this framework process inherited values


.. _tutorials_advancedusage_missing:

Process missing values
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: introduce how this framework process key missing situation


Functional utilities
~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: writing mapping, filter, mask, shrink here

Structural utilities
~~~~~~~~~~~~~~~~~~~~

.. todo:: writing union, subside, rise here

Tree utilities
~~~~~~~~~~~~~~~~~~

.. todo:: writing jsonify, view, clone, typetrans here

Decorators
~~~~~~~~~~~~~~

.. todo:: writing func_treelize, method_treelize and classmethod_treelize, \
    method_treelize is also supported to property getter.

DIY new treevalue class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: introduce general_treelize here, especially how to support add.

Other
~~~~~~~~~~~~~~~~~~~~



