Architecture
=============================

In this part, the generic architecture of tree value will be introduced.
You can try to understand its core ideas by reading this page.

Like that in numpy and pytorch, tree value's data layer and logic layer are separated with each other.
The data layer is called `Tree` and the logic layer is called `TreeValue`.
One or more tree values may be pointed to one tree, they share the same memory.
In order to support the tree-to-tree operations (tree-to-value or value-to-value are special cases of tree-to-tree) ,\
`func_treelize` are provided to transform a common value-based function to a tree-based function.

The core architecture is like this:

.. image:: architecture.puml.svg
    :align: center

Tree
---------


TreeValue
---------------


func_treelize
-------------------


