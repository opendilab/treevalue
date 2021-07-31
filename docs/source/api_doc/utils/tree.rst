treevalue.utils.tree
==========================

build_tree
-----------------

.. autofunction:: treevalue.utils.tree.build_tree


build_graph
~~~~~~~~~~~~~~~~~~~

.. autofunction:: treevalue.utils.tree.build_graph

Here is an example of `build_graph` function. The source code is

.. literalinclude:: build_graph.demo.py
    :language: python
    :linenos:

The generated graphviz source code should be

.. literalinclude:: build_graph_demo.dat.gv
    :language: text
    :linenos:

The graph should be

.. image:: build_graph_demo.dat.gv.svg
    :align: center

Also, multiple rooted graph is supported, this function will detect
the pointer of the objects. Just like another complex source code below.

.. literalinclude:: build_graph_complex.demo.py
    :language: python
    :linenos:

The exported graph should be

.. image:: build_graph_complex_demo.dat.gv.svg
    :align: center
