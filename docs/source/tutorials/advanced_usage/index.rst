Advanced Usage
===================

In this part, Some of the advanced usages of ``TreeValue`` \
will be introduced one by one with sample code and \
graph to explain them.

For further information or usage of ``TreeValue`` and ``FastTreeValue``, \
you may take a look at the following pages:

* ``TreeValue`` and its utilities: :doc:`../../api_doc/tree/tree`.
* ``func_treelize`` and other wrappers: :doc:`../../api_doc/tree/func`.
* ``FastTreeValue`` and its operators, methods: :doc:`../../api_doc/tree/general`.

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

The mode argument is the most important argument in function ``func_treelize``. \
For it depends the basic logic of the graph calculation.

The type of ``mode`` argument is ``TreeMode``, which documentation is like this.

.. autoenum:: treevalue.tree.func.TreeMode
    :noindex:

In this part, all of the 4 modes will be introduced \
with details and samples one by one.

Strict Mode
~~~~~~~~~~~~~~~~~

Strict mode is the most frequently-used mode in real cases. \
It is also the default value of the ``mode`` argument in the \
treelize functions.

To be simple, strict mode need the keys of a node in the tree \
be strictly mapped one by one, missing or overage of the keys \
are both forbidden in strict mode, which means ``KeyError`` will \
be raised.

For example, in the trees in ``strict_demo_1``, \
if we need to added ``t1`` and ``t2`` together, ``t3`` will be the result. \
Because all the keys (``a``, ``b``, ``x`` of the root nodes, \
and ``c``, ``d``, ``e`` of the ``x`` node) can be mapped one by one.

.. image:: strict_demo_1.gv.svg
    :align: center

In another situation, when the keys are not so regular like \
that in ``strict_demo_1``, like the trees in ``strict_demo_2``. \
If we try to add ``t1`` and ``t2`` in strict mode, ``KeyError`` will \
be raised due to the missing of key ``a`` in ``t1`` and key ``f`` in `t2.x`.

.. image:: strict_demo_2.gv.svg
    :align: center

Here is a real code example of strict mode.

.. literalinclude:: strict_demo.demox.py
    :language: python
    :linenos:

The stdout and stderr should like below, \
a ``KeyError`` is raised at the second ``print`` statement.

.. literalinclude:: strict_demo.demox.py.txt
    :language: text
    :linenos:

.. literalinclude:: strict_demo.demox.py.err
    :language: text
    :linenos:

.. _tutorials_advancedusage_how_works:

.. note::

    How does the treelized function work?

    Here is another example which show the actual calculation \
    process of the wrapped function.

    .. literalinclude:: strict_demo_show.demox.py
        :language: python
        :linenos:

    In this code, once the original function ``plus`` is called, \
    the actual value of argument ``a`` and ``b`` will be printed to \
    stdout.

    In the ``plus(t1, t2)``, all the calculation can be carried \
    on because add operator between primitive ``int`` and \
    ``np.ndarray`` is supported, so no error occurs and \
    the result of ``+`` between ``int`` and ``np.ndarray`` will \
    be one of the values of the result tree.

    But in ``plus(t1, t3)``, when get the result of \
    ``plus(t1, t3).b``, it will try to add ``t1.b`` and \
    ``t2.b`` together, but there is no implement of operator \
    ``+`` between primitive ``int`` and ``list`` objects, so \
    ``TypeError`` will be raised when do this calculation.

    The complete stdout and stderr should be like this.

    .. literalinclude:: strict_demo_show.demox.py.txt
        :language: text
        :linenos:

    .. literalinclude:: strict_demo_show.demox.py.err
        :language: text
        :linenos:

In strict mode, missing or overage of keys are not tolerated \
at all. So in some of the cases, especially when you can not \
suppose that all the trees involved in calculation has \
exactly the same structure. Based on this demand, left mode, \
inner mode and outer mode is designed, and they will be \
introduced with details and examples in the next 3 sections.

Left Mode
~~~~~~~~~~~~~~~~

In left mode, the result tree's key set will be aligned to the \
first tree from the left.

In the trees in ``left_demo_1``, ``t3`` is the plus result of ``t1`` \
and ``t2``. We can see that `t2.a` is ignored \
because of `t1.a` 's non-existence. Finally no error will be \
raised, the calculation will be processed properly with the \
tree structure of ``t1``.

.. image:: left_demo_1.gv.svg
    :align: center

But in the ``left_demo_2`` (actually it is exactly \
the same as ``strict_demo_2``), ``KeyError`` will be raised \
because `t2.x.f`` not found in tree ``t2`, so the result \
can not be aligned to tree ``t1``, calculation failed.

.. image:: left_demo_2.gv.svg
    :align: center

When you decorate a function as left mode, the decorated function \
will try to find the first tree from left. If there is no less than \
1 positional arguments detected, the first positional argument \
will be used as the left tree. Otherwise, \
the tree with the smallest lexicographic key will be assigned \
as the left tree. Obviously, As least 1 positional or \
key-word-based argument should be in the arguments.

Here is a real code example of left mode.

.. literalinclude:: left_demo.demox.py
    :language: python
    :linenos:

The stdout and stderr should like below, \
a ``KeyError`` is raised at the second ``print`` statement.

.. literalinclude:: left_demo.demox.py.txt
    :language: text
    :linenos:

.. literalinclude:: left_demo.demox.py.err
    :language: text
    :linenos:

In the code example above, the result is aligned to \
tree ``a`` in wrapped function ``plus``. So the first plus \
calculation will get the proper result, but the second one \
will fail.

Inner Mode
~~~~~~~~~~~~~~~~~~~~

In inner mode, the result tree's key set will be aligned \
to the intersection set of all the tree's key set in arguments.

In the trees in ``inner_demo_1``, ``t3`` is the plus result of ``t1`` \
and ``t2``. We can see that ``t2.a`` and ``t1.x.f`` is ignored \
because of ``t1.a``  and ``t2.x.f``'s non-existence. Finally \
no error will be raised, the calculation will be processed \
properly with the tree structure of the intersection between \
tree ``t1`` and ``t2``.

.. image:: inner_demo_1.gv.svg
    :align: center

In most cases of inner mode (HansBug says that he failed \
to construct even one case of inner mode's structural failure), \
the calculation will be processed properly because of the \
intersection operation on the key set and key missing or \
overage are both avoided completely. But the shortage of \
inner mode is the loss of some information, for keys and its \
value or subtrees will be directly ignored without any warning. \
So **before using inner mode, please confirm that you know its \
running logic**.

Here is a real code example of inner mode.

.. literalinclude:: inner_demo.demo.py
    :language: python
    :linenos:

The stdout (no stderr content in this case) should like below, \
no errors occurred with exit code 0.

.. literalinclude:: inner_demo.demo.py.txt
    :language: text
    :linenos:


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



