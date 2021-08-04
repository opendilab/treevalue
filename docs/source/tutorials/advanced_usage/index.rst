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

In the primitive python, some convenient functional operations \
are supported, such as

.. literalinclude:: functional_python_demo.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: functional_python_demo.demo.py.txt
    :language: text
    :linenos:

Actually, functional operations are supported in tree values \
as well, and they will be introduced in this section.

Mapping
~~~~~~~~~~~~~~~~~~

Mapping function is similar to the primitive ``map`` function. \
The relation between ``TreeValue`` and ``mapping`` function \
is like that between ``list`` and ``map`` function.

Here is a simple real code example

.. literalinclude:: mapping_demo.demo.py
    :language: python
    :linenos:

The mapped tree result should be like below.

.. literalinclude:: mapping_demo.demo.py.txt
    :language: text
    :linenos:

For further definition or source \
code implement of function ``mapping``, \
take a look at :ref:`apidoc_tree_tree_mapping`.

Filter
~~~~~~~~~~~~~

Filter function is similar to the primitive ``filter`` \
function. The relation between ``TreeValue`` and ``filter_`` \
function is like that between ``list`` and ``filter`` function .

Here is a simple real code example

.. literalinclude:: filter_demo.demo.py
    :language: python
    :linenos:

The filtered tree result should be like below. \
When ``remove_empty`` is disabled, the empty tree node will \
be kept to make sure the structure of the result tree is \
similar to the unfiltered tree.

.. literalinclude:: filter_demo.demo.py.txt
    :language: text
    :linenos:

.. note::
    Actually, the code above is equal to the code below. \
    The ``filter_`` function can be seen as a combination \
    of ``mask`` function and ``mapping`` function.

    .. literalinclude:: filter_eq_demo.demo.py
        :language: python
        :linenos:

    The result should be like below, exactly the same as \
    the code above.

    .. literalinclude:: filter_eq_demo.demo.py.txt
        :language: text
        :linenos:

    For further information about ``mask`` function, \
    take a look at :ref:`tutorials_advancedusage_functional_mask`.

For further definition or source \
code implement of function ``filter_``, \
take a look at :ref:`apidoc_tree_tree_filter`.

.. _tutorials_advancedusage_functional_mask:

Mask
~~~~~~~~~~~~~~~

Mask function allow your choice in one tree, by another tree \
of true-or-false flags. A simple code example is

.. literalinclude:: mask_demo.demo.py
    :language: python
    :linenos:

The result will be like below, values mapped with the tree \
``m`` which mask flag is ``False`` are all deleted. Also, \
``remove_empty`` argument is supported.

.. literalinclude:: mask_demo.demo.py.txt
    :language: text
    :linenos:

For further definition or source \
code implement of function ``mask``, \
take a look at :ref:`apidoc_tree_tree_mask`.

Reduce
~~~~~~~~~~~~~~~~~~~~

By using ``reduce_`` function, you can get some calculation \
result based on the tree structure. Its meaning is similar \
to primitive ``reduce_`` function, but its base structure is \
``TreeValue`` instead of sequence or iterator. For example, \
we can get the sum and multiply accumulation of the values \
in the tree.

.. literalinclude:: reduce_demo_1.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: reduce_demo_1.demo.py.txt
    :language: text
    :linenos:

If we use ``reduce_`` function with ``mapping`` function, \
huffman weight sum can also be easily calculated with \
the code below.

.. literalinclude:: reduce_demo_2.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: reduce_demo_2.demo.py.txt
    :language: text
    :linenos:

Besides, we can easily calculate sum of the ``np.ndarray`` \
objects' bytes size, like the following code.

.. literalinclude:: reduce_demo_3.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: reduce_demo_3.demo.py.txt
    :language: text
    :linenos:

For further definition or source \
code implement of function ``reduce_``, \
take a look at :ref:`apidoc_tree_tree_reduce`.

Structural Utilities
--------------------

In order to process some structured data, especially when \
you need to process a sort of ``TreeValue`` objects which is \
in the primitive collections or mappings, the structural \
utilities are designed, and they will be introduced in \
this section with examples.

Union
~~~~~~~~~~~~~~~~~~~~~~

The ``union`` function is similar to the primitive \
``zip`` function some ways, it can combine a list of \
``TreeValue`` objects as one ``TreeValue`` object which \
leaf values are tuples, like the simple example below.

.. literalinclude:: union_demo.demo.py
    :language: python
    :linenos:

The result should be like below, the leaf values are \
unionised as tuples.

.. literalinclude:: union_demo.demo.py.txt
    :language: text
    :linenos:

.. note::
    In ``union`` function (actually ``subside`` function \
    has the same property), all the trees to be unionised \
    need to have the same structure. You can just \
    consider it as strict mode with inheriting is enabled.

For further information and arguments of function ``union``, \
take a look at :ref:`apidoc_tree_tree_union`.

Subside
~~~~~~~~~~~~~~~~~~~~

The ``subside`` function can transform the collections or \
mapping nested ``TreeValue`` objects into one ``TreeValue`` \
object which leaf values has the dispatch's structure. \
The ``union`` function mentioned above is also based on \
the ``subside`` function. Function ``subside`` will greatly \
simplify the code when the structured data need to be \
calculated. Just like this following example code.

.. literalinclude:: subside_demo.demo.py
    :language: python
    :linenos:

The result should be like below, the leaf values are \
combined as the dispatch structure of ``st``.

.. literalinclude:: subside_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    In function ``subside``, only primitive list, tuple \
    and dict (or subclasses) objects will be subsided to \
    leaf values.

For further information and arguments of function ``subside``, \
take a look at :ref:`apidoc_tree_tree_subside`.


Rise
~~~~~~~~~~~~~~~~

Function ``rise`` can be seen as the inverse operation of \
function ``subside``, it will try to extract the greatest \
common structure of the leaf values, and rise them up to \
the dispatch above the ``TreeValue`` objects. \
Like the following example code.

.. literalinclude:: rise_demo_1.demo.py
    :language: python
    :linenos:

The result should be like below, the subsided tree ``st`` \
can be extract back to the original structure.

.. literalinclude:: rise_demo_1.demo.py.txt
    :language: text
    :linenos:

.. note::

    In function ``rise``, only primitive list, tuple \
    and dict (or subclasses) objects will join the \
    rising operation.

    Actually, when ``template`` argument is not assigned, \
    the ``rise`` function will try to find the greatest \
    common structure and rise them to the dispatch. The \
    following rules will be strictly followed when doing \
    this:

    * If the values in current level have the same type ( \
      must all be list, all be tuple or all be dict), the \
      rising function will carry on the find sub structure, \
      otherwise values in current level will be treated as \
      atomic values.
    * If all of them are dicts, and they have exactly the \
      same key sets with each other, the finding of sub \
      structures will be carried on, otherwise these dicts will \
      be treated as atomic values.
    * If all of them are lists, and they have the same length \
      with each other, the finding of sub structures \
      will be carried on, otherwise these dicts will \
      be treated as atomic values.
    * If all of them are tuples, and they have the same length \
      with each other, the finding of sub structures \
      will be carried on, otherwise these dicts will \
      be treated as atomic values. (Actually, this rule \
      is the same as the last one which is about lists.)

    Considering this automatic structure finding process, \
    if you only want to extract some of the structure (\
    make sure the extraction will not be too deep or too \
    shallow, and make sure the result will have the same \
    structure as your expectation), you can assign value in \
    ``template`` arguments. Like the example code below.

    .. literalinclude:: rise_demo_2.demo.py
        :language: python
        :linenos:

    The result should be like below, \
    the subsided tree ``st`` can be extract back \
    to the structure of dict with only ``first`` \
    and ``second`` keys.

    .. literalinclude:: rise_demo_2.demo.py.txt
        :language: text
        :linenos:

For further information and arguments of function ``rise``, \
take a look at :ref:`apidoc_tree_tree_rise`.

Tree Utilities
------------------

In this section, utilities with ``TreeValue`` class and \
its objects themselves will be introduced with examples.

Jsonify
~~~~~~~~~~~~~~~~~~~

With the usage of ``jsonify`` function, you can \
transform a ``TreeValue`` object to json-formatted data.

For example, the following real code

.. literalinclude:: jsonify_demo.demo.py
    :language: python
    :linenos:

The result should be

.. literalinclude:: jsonify_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    The function ``raw`` in the example code above is \
    a wrapper for dictionary object. It can be used to \
    pass ``dict`` object as simple value in ``TreeValue`` \
    instead of being treated as sub tree.

    For further information of function ``raw``, \
    take a look at :ref:`apidoc_tree_common_raw`.

For further informaon of function ``jsonify``, \
take a look at :ref:`apidoc_tree_tree_jsonify`.

View
~~~~~~~~~~~~~

Another magic function named ``view`` is also provided, \
to process logic viewing cases.

.. literalinclude:: view_demo.demo.py
    :language: python
    :linenos:

The result will be like below, ``t_x_y`` and ``vt_x_y``'s \
value is different after the replacement of the sub tree \
named ``t.x``, for ``vt_x_y``'s value's equality to the \
current ``t.x.y``.

.. literalinclude:: view_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    Attention that the ``view`` operation is different \
    from sub node getting operation. In viewed tree, \
    it is based on a logic link based on the tree be viewed, \
    and the actual operations are performed in the actual \
    tree node. The main difference between ``view`` and \
    getting sub node is that the view tree will be \
    affected by the replacement of sub nodes in viewed tree.

    Like the code example above, in the view tree ``vt_x_y``, \
    before do tree operations, the viewed tree will \
    be approached from root tree ``t`` by keys of ``x`` and \
    ``y``, so after the replacement of the whole subtree \
    ``t.x``, ``vt_x_y`` is still the latest value of ``t.x.y``, \
    while ``t_x_y`` is still the old sub tree of tree ``t``, \
    before replacement.


For further informaon of function ``view``, \
take a look at :ref:`apidoc_tree_tree_view`.

Clone
~~~~~~~~~~~~~~~~

The ``TreeValue`` objects can be cloned deeply by \
``clone`` function.

.. literalinclude:: clone_demo.demo.py
    :language: python
    :linenos:

The result will be like below, all the memory address \
of the tree nodes in cloned tree are different from \
those in the original tree ``t`` when ``copy_value`` \
argument is not set. But when ``copy_value`` is assigned \
as ``True``, the address of values will be changed because \
of the deep copy of value.

.. literalinclude:: clone_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    Attention that in function ``clone``, the values \
    will not be deeply copied together with \
    the tree nodes by default. **The newly cloned \
    tree's values have the same memory \
    address with those in original tree**.

    If deep copy of values is required when using ``clone``, \
    ``copy_value`` argument need to be assigned as ``True``. \
    And then a ``copy.deepcopy`` will be performed in \
    ``clone`` function in order to do the deep copy. \
    Also, you can define your own copy function in \
    ``copy_value`` argument by just assign it as \
    a lambda expression \
    like ``lambda x: pickle.loads(pickle.dumps(x))``.

For further informaon of function ``clone``, \
take a look at :ref:`apidoc_tree_tree_clone`.

Typetrans
~~~~~~~~~~~~~~~

You can use function ``typetrans`` to change the type of \
tree value object, just like the example below.

.. literalinclude:: typetrans_demo.demo.py
    :language: python
    :linenos:

The result will be like below. After the type transformation, \
``**`` operator can not be used in ``t2`` but method ``pw`` \
which is implemented in ``MyTreeValue`` will be enabled.

.. literalinclude:: typetrans_demo.demo.py.txt
    :language: text
    :linenos:

.. note::

    In treevalue library, there can be more classes \
    based on ``TreeValue`` class by your definition.

    Different tree value class will have the different \
    operators, methods and class methods for service, and \
    the ``__eq__`` operator's result between different \
    type of tree values will always be ``False`` because of \
    the difference of their types.

    For further information of ``TreeValue`` class and \
    user's definition practice, just take a look at:

    * :ref:`API documentation of TreeValue<apidoc_tree_tree_treevalue>`.
    * :ref:`API documentation of FastTreeValue<apidoc_tree_general_fasttreevalue>`.
    * :ref:`tutorials_advancedusage_diy`.

For further informaon of function ``typetrans``, \
take a look at :ref:`apidoc_tree_tree_typetrans`.


Object Oriented Usage
----------------------------

In ``FastTreeValue`` class, plenty of object-oriented \
operators, methods and classmethods are supported in order \
to simplify the actual usage. Here is a simple code example.

.. literalinclude:: oo_demo.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: oo_demo.demo.py.txt
    :language: text
    :linenos:

For further information of ``FastTreeValue`` class, \
take a look at :ref:`apidoc_tree_general_fasttreevalue`, \
all the supported methods and operators are listed here.


.. _tutorials_advancedusage_diy:

DIY TreeValue Class
-----------------------------

You can define your own ``TreeValue`` class with \
your own method and class methods. Like the \
example code below.

.. literalinclude:: diy_class_demo.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: diy_class_demo.demo.py.txt
    :language: text
    :linenos:

For further information of function ``method_treelize`` \
and ``classmethod_treelize``, just take a look at:

* :ref:`apidoc_tree_func_methodtreelize`
* :ref:`apidoc_tree_func_classmethodtreelize`



DIY TreeValue Utility Class
-------------------------------

You can define a pure utility class in with function \
``utils_class`` and ``classmethod_treelize``. Like the \
following example code.

.. literalinclude:: utils_demo.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: utils_demo.demo.py.txt
    :language: text
    :linenos:

For further information of function ``utils_class`` \
and ``classmethod_treelize``, just take a look at:

* :ref:`apidoc_tree_func_utilsclass`
* :ref:`apidoc_tree_func_classmethodtreelize`


Draw Graph For TreeValue
-----------------------------

You can easily draw a graph of the ``TreeValue`` objects \
with function ``graphics``. Like the following example \
code.

.. literalinclude:: ../../api_doc/tree/graphics.demo.py
    :language: python
    :linenos:

The generated code and graph should be like below

.. literalinclude:: ../../api_doc/tree/graphics.dat.gv
    :language: text
    :linenos:

.. image:: ../../api_doc/tree/graphics.dat.gv.svg
    :align: center

.. note::

    The return value's type of function ``graphics`` is \
    class ``graphviz.dot.Digraph``, from the opensource \
    library ``graphviz``, for further information of \
    this project and ``graphviz.dot.Digraph``'s usage, \
    take a look at:

    * `Official site of Graphviz <https://graphviz.org/>`_.
    * `User Guide of Graphviz <https://graphviz.readthedocs.io/en/stable/manual.html#formats>`_.
    * `API Reference of Graphviz <https://graphviz.readthedocs.io/en/stable/api.html>`_.

For further information of function ``graphics``, \
just take a look at

* :ref:`apidoc_tree_tree_graphics`.
