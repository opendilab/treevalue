Architecture
=============================

In this part, the generic architecture of tree value will be introduced.
You can try to understand its core ideas by reading this page.

Like that in numpy and pytorch, tree value's data layer and logic layer are separated with each other.
The data layer is called ``Tree`` and the logic layer is called ``TreeValue``.
One or more tree values may be pointed to one tree, they share the same memory.
In order to support the tree-to-tree operations (tree-to-value or value-to-value are special cases of tree-to-tree) ,\
``func_treelize`` are provided to transform a common value-based function to a tree-based function.

The core architecture is like this:

.. image:: architecture.puml.svg
    :align: center

Tree
---------

``Tree`` class is the data layer of the ``TreeValue``. \
The relation with ``Tree`` and ``TreeValue`` is similar to \
that of ``torch.Tensor`` and ``torch.Buffer``. \
Actually, there can be multiple ``TreeValue`` nodes pointed \
at the same ``Tree`` node, they will share the same memory \
and when one the them are modified, the other ``TreeValue`` \
pointed at the same position will be effected all at a time.

Here is a example with the usage of the same memories.

.. literalinclude:: tree_demo.demo.py
    :language: python
    :linenos:

The output is like the following, you can see the memory \
address of ``t1`` and ``t2`` are the same, when ``t1`` \
is updated, ``t2`` will be changed together.

.. literalinclude:: tree_demo.demo.py.txt
    :language: text
    :linenos:

For contributor, you can get the tree instance inside of \
a ``TreeValue`` instance, by using ``get_property_data`` \
function, like the following code.

.. literalinclude:: get_tree_demo.demo.py
    :language: python
    :linenos:

.. literalinclude:: get_tree_demo.demo.py.txt
    :language: text
    :linenos:

Not only the native ``Tree`` class is provided, \
``TreeView`` class is also provided for processing the \
tree view cases. They have the same methods and interface \
(actually they are both inherited from ``BaseTree`` class), \
so they are compatible with each other. The class \
``Tree`` and ``TreeView`` form the data layer of \
``TreeValue``.

* :ref:`API documentation of BaseTree<apidoc_tree_common_basetree>`.
* :ref:`API documentation of Tree<apidoc_tree_common_tree>`.
* :ref:`API documentation of TreeView<apidoc_tree_common_treeview>`.

TreeValue
---------------

The ``TreeValue`` is the logic layer, all the operations \
and calculations are performed on this layer.

There are 2 primitive ``TreeValue`` classes in this project, \
which are called ``TreeValue`` and ``FastTreeValue``. \
In class ``TreeValue``, only the least necessary features \
are implemented, while the common and frequently-used \
features are all implement in the ``FastTreeValue``, which \
inherits from ``TreeValue``.

When coding, if you need to define a kind of tree which \
has the common convenient features, just implement \
class ``FastTreeValue`` or use function ``general_tree_value`` \
is okay. But if you need to define your own operations \
from an empty template, just inherit the raw ``TreeValue`` class.

For further information of ``TreeValue``, take a look \
at:

* :ref:`Definition of TreeValue<tutorials_mainidea_definition_treevalue>`.
* :ref:`API documentation of TreeValue<apidoc_tree_tree_treevalue>`.
* :ref:`API documentation of FastTreeValue<apidoc_tree_general_fasttreevalue>`.
* :ref:`API documentation of general_tree_value<apidoc_tree_general_generaltreevalue>`.

func_treelize
-------------------

Function ``func_treelize`` is the core feature of this project, \
almost all the convenient calculations and operations \
are based on this function.

For further information of ``func_treelize``, take a look \
at the following pages and their source code implements:

* :ref:`Definition of treelize<tutorials_mainidea_definition_treelize>`.
* :ref:`API documentation of func_treelize<apidoc_tree_func_functreelize>`.
* :ref:`API documentation of method_treelize<apidoc_tree_func_methodtreelize>`.
* :ref:`API documentation of classmethod_treelize<apidoc_tree_func_classmethodtreelize>`.
