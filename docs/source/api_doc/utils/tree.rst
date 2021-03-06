treevalue.utils.tree
==========================

.. py:currentmodule:: treevalue.utils.tree

.. automodule:: treevalue.utils.tree

build_graph
-------------------

.. autofunction:: build_graph

Here is an example of ``build_graph`` function. The source code is

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

The return value's type of function ``graphics`` is \
class ``graphviz.dot.Digraph``, from the opensource \
library ``graphviz``, for further information of \
this project and ``graphviz.dot.Digraph``'s usage, \
take a look at:

* `Official site of Graphviz <https://graphviz.org/>`_.
* `User Guide of Graphviz <https://graphviz.readthedocs.io/en/stable/manual.html#formats>`_.
* `API Reference of Graphviz <https://graphviz.readthedocs.io/en/stable/api.html>`_.
