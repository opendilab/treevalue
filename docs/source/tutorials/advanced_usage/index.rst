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

.. _tutorials_advancedusage_modes:

Function Modes
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

.. note::
    In most cases of inner mode, \
    the calculation will be processed properly because of the \
    intersection operation on the key set and key missing or \
    overage are both avoided completely.

    But the shortage of inner mode is the loss of \
    some information, for keys and its value or subtrees \
    will be directly ignored without any warning. So \
    **before using inner mode, please confirm that you \
    know its running logic and the missing of some nodes**.

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

In outer mode, the result tree's key set will be aligned to \
the union set of the tree's key set in arguments.

In the trees in ``outer_demo_1``, ``t3`` is the plus result of \
``t1`` and ``t2``, with the missing value of ``0``. We can see \
that all the values in tree ``t1`` and ``t2`` are involved \
in this calculation, and because of the missing of ``t1.a`` and \
``t2.x.f`` they will be actually treated as ``0`` in \
calculation process. Finally no error will be raised, and \
sum of the tree nodes' value will form the result tree ``t3``.

.. image:: outer_demo_1.gv.svg
    :align: center

.. note::
    In outer mode, it is strongly recommended to set the \
    value of argument ``missing``. When ``missing``'s \
    value is not set and there are key missing in \
    some of the argument trees, ``KeyError`` will be raised
    due to this missing and value of ``missing``.

    For further information and examples of ``missing`` \
    argument, take a look at
    :ref:`tutorials_advancedusage_missing`.

Here is a real code example of inner mode.

.. literalinclude:: outer_demo.demo.py
    :language: python
    :linenos:

The stdout (no stderr content in this case) should like below, \
no errors occurred with exit code 0.

.. literalinclude:: outer_demo.demo.py.txt
    :language: text
    :linenos:


.. _tutorials_advancedusage_inherit:

Inheriting on Trees
-------------------

Inheriting is another important feature of treelize functions. \
It will be introduced in this section with necessary examples.

In some cases, we need to calculation between values with \
different dimensions, such as in ``numpy``, you can add \
primitive integer with a ``ndarray`` object, like this

.. literalinclude:: inherit_numpy_demo.demo.py
    :language: python
    :linenos:

The result will be like below, result of ``ar1 + 9`` is \
actually the same as the result of \
expression ``ar1 + np.array([[9, 9], [9, 9]])``.

.. literalinclude:: inherit_numpy_demo.demo.py.txt
    :language: text
    :linenos:

In treelize functions, you can achieve this processing way \
by use the ``inherit`` argument. Considering this situation \
can be find almost anywhere, so the default value of \
``inherit`` argument is ``True``, which means the inheriting \
option is on by default.

We can see the example in ``inherit_demo_1``, the tree ``t1`` \
and tree ``t2`` have different structures, and cannot be \
processed by any modes in :ref:`tutorials_advancedusage_modes`, \
because ``t1.x`` is a primitive integer value but ``t2.x`` is \
a subtree node, their types are structurally different.

.. image:: inherit_demo_1.gv.svg
    :align: center

But when inheriting is enabled, this adding operation can \
still be carried on, for the value of ``t1.x`` (is ``9`` \
in ``inherit_demo_1``) will be applied to the whole \
subtree ``t2.x``, like the result tree ``t3`` shows. \
The result of tree ``t3.x`` can be considered as the sum \
of primitive integer ``9`` and subtree ``t2.x``.

Based on the structural properties above, in the example of \
``inherit_demo_2``, a primitive value can be directly added \
with a complete tree, like the result \
tree ``t2 = t1 + 5`` shows.

.. image:: inherit_demo_2.gv.svg
    :align: center

When inheriting is disabled, all the cases with primitive value \
and tree node at the same path position will cause ``TypeError``. \
For example, when inheriting is disabled, ``inherit_demo_1`` \
and ``inherit_demo_2`` will failed, but ``strict_demo_1`` will \
still success because no primitive value appears at the same \
path position of tree node.

.. image:: strict_demo_1.gv.svg
    :align: center

Here is a real code example of inheriting.

.. literalinclude:: inherit_demo.demox.py
    :language: python
    :linenos:

The stdout and stderr should be like below, the the \
calculation of ``plus`` function and the first calculation \
of ``plusx`` function will be processed properly, but the \
last one will failed due to the disablement of inheriting.

.. literalinclude:: inherit_demo.demox.py.txt
    :language: text
    :linenos:

.. literalinclude:: inherit_demo.demox.py.err
    :language: text
    :linenos:

.. note::

    In most cases, disablement of inheriting is not recommended \
    because it will cause some errors. Disable inheriting can \
    increase the structural strictness of calculation, \
    but all the cross-dimensional tree operation will be \
    forbidden as well.

    So before disabling inheriting, make sure you know well \
    about what you are going to do.

.. _tutorials_advancedusage_missing:

Process Missing Values
--------------------------

In some cases of left mode and outer mode, some of keys in \
result tree can not find the node nor value at the \
corresponding path position in some of the argument trees. \
In order the make these cases be processable, missing value \
can be used by setting value or lambda expression in ``missing`` \
argument.

Just like the example ``outer_demo_1`` mentioned forwards, \
when ``t1.a`` and ``t2.x.f`` not found in trees, the given \
missing value ``0`` will be used instead.

.. image:: outer_demo_1.gv.svg
    :align: center

Another case is the ``missing_demo_1`` which is based \
on left mode. In this case, ``t2.a`` is ignore due to the \
property of left mode, ``t2.x.f`` is missing but ``t1.x.f`` \
can be found, so ``t2.x.f`` will use the missing value ``0``. \
Finally, ``t3`` will be the result of left addition of ``t1`` \
and ``t2``, with missing value of ``0``.

.. image:: missing_demo_1.gv.svg
    :align: center

Considering another complex case, when the values of tree are \
primitive lists, like the ``missing_demo_2`` which is based on \
outer mode. At this time, if we need to do addition with \
missing value supported, we can set the missing value to \
an empty list. The result is like below.

.. image:: missing_demo_2.gv.svg
    :align: center

.. note::
    In ``missing_demo_2``, ``lambda :[]`` will be the \
    value of ``missing`` argument in actual code.

    In ``missing`` argument, its value will be automatically \
    executed when it is callable, and its execution's return \
    value will be the actual missing value.

    By passing a lambda expression in, you can construct a \
    new object everytime missing value is required, and the \
    duplication of the missing value's object will be avoided. \
    So it is not recommended to use ``missing`` argument like \
    ``[]``, ``{}`` or ``myobject()`` in python code, but \
    ``lambda :[]``, ``lambda :{}`` and ``lambda :myobject()`` \
    are better practices.

Here is a real code example of missing_value.

.. literalinclude:: missing_demo.demo.py
    :language: python
    :linenos:

The stdout (no error occurred) should be like below, \
the calculation of ``plus`` function  will be processed \
properly, like the result in ``missing_demo_2``.

.. literalinclude:: missing_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    Missing value will be only applied in left mode and outer mode.

    In strict mode, missing or overage of keys are absolutely \
    not tolerated, missing value will make no sense and a \
    ``RuntimeWarning`` will be logged.

    In inner mode, missing value will never be actually \
    in use because all the key sets of final result are \
    intersection set of argument trees. There will never be \
    any key missing cases at all when inner mode is used, \
    a ``RuntimeWarning`` will be logged with the usage of \
    missing value in inner mode.


Functional Utilities
-----------------------

.. todo:: writing mapping, filter, mask, shrink here

Structural Utilities
--------------------

.. todo:: writing union, subside, rise here

Tree Utilities
------------------

.. todo:: writing jsonify, view, clone, typetrans here

Treelize Decorators
-------------------------

.. todo:: writing func_treelize, method_treelize and classmethod_treelize, \
    method_treelize is also supported to property getter.

DIY new treevalue class
-----------------------------

.. todo:: introduce general_treelize here, especially how to support add.

Other
--------------------



