Basic Usage
=====================

In this part, basic usages of ``TreeValue`` will be introduced one \
by one with sample code and graph to explain them.

Create a tree
-----------------

You can easily create a tree value object based on ``FastTreeValue``.

.. literalinclude:: ../quick_start/create_a_tree.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: ../quick_start/create_a_tree.demo.py.txt
    :language: text
    :linenos:


Edit the tree
------------------

After the tree is created, you can access and edit it with ``__getattr__``, ``__setattr__`` and ``__delattr__``.

.. literalinclude:: edit_tree.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: edit_tree.demo.py.txt
    :language: text
    :linenos:

The values on the tree has been changed or deleted properly.
And the full life circle of the tree ``t`` is like below.

.. image:: edit_tree_1.gv.svg
    :align: center

.. image:: edit_tree_2.gv.svg
    :align: center

Do index or slice calculation on the tree
------------------------------------------------

Index and slice index operation can be applied all once, like the example below.

.. literalinclude:: index_and_slice.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: index_and_slice.demo.py.txt
    :language: text
    :linenos:

The structures oof the trees is like the graph below.

.. image:: index_operation.gv.svg
    :align: center

.. image:: slice_index_operation.gv.svg
    :align: center


Do calculation on the tree
------------------------------

Common calculation is supported in treevalue.

.. literalinclude:: calculation.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: calculation.demo.py.txt
    :language: text
    :linenos:

The values is processed one to one between the tree.
The structures of the trees involved in ``__add__`` calculation is like below.

.. image:: calculation_add.gv.svg
    :align: center

.. image:: calculation_sub_and_xor.gv.svg
    :align: center

Actually, More common operators are supported in treevalue.

.. note::

    In newer versions of treevalue, self operations \
    are supported like the code below.

    .. literalinclude:: calculation_self.demo.py
        :language: python

    The output should be

    .. literalinclude:: calculation_self.demo.py.txt
        :language: text

    We can see that when ``t1 + t2`` is called, \
    a new tree with the sums will be created \
    without ``t1``'s change, but when ``t1 += t2`` is called, \
    the values in ``t1`` will be replaced to the sums.

.. _tutorials_basicusage_func:

Make function tree supported
-----------------------------------

Sometimes we need to do some complex calculation \
which are not able to be represented by raw operators.

In this situation, we can wrap the common function \
to tree supported function like the code below.

.. literalinclude:: tree_support.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: tree_support.demo.py.txt
    :language: text
    :linenos:

Luckily, the wrapped function can still used \
as the original function as well.

The structure of the trees in this part is like below.

.. image:: tree_support_1.gv.svg
    :align: center

.. image:: tree_support_2.gv.svg
    :align: center

Besides, the ``func_treelize`` function will never change the \
original logical properties of the original function. In the \
example below, the calculation with original values instead of \
usage of the trees can be processed properly with the \
result of the primitive value.

.. literalinclude:: tree_support_primitive.demo.py
    :language: python
    :linenos:

The output should be like below, the ``gcd`` **function can \
still support the greatest common divisor of the primitive \
integers**.

.. literalinclude:: tree_support_primitive.demo.py.txt
    :language: text
    :linenos:

For further information of how the tree-supported function works, take a look \
at :ref:`How the treelized function works<tutorials_advancedusage_how_works>` , \
this note may give you more information.

