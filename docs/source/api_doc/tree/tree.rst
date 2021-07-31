treevalue.tree.tree
======================

TreeValue
---------------

.. autoclass:: treevalue.tree.tree.tree.TreeValue
    :members: __init__, __getattr__, __setattr__, __delattr__, __contains__, __repr__, __iter__, __hash__, __eq__, _attr_extern, __len__, __bool__, __str__, __getstate__, __setstate__


jsonify
--------------

.. autofunction:: treevalue.tree.tree.utils.jsonify


view
----------

.. autofunction:: treevalue.tree.tree.utils.view


clone
-----------

.. autofunction:: treevalue.tree.tree.utils.clone


typetrans
------------------

.. autofunction:: treevalue.tree.tree.utils.typetrans


mapping
--------------

.. autofunction:: treevalue.tree.tree.utils.mapping


mask
-------------------

.. autofunction:: treevalue.tree.tree.utils.mask


filter\_
----------------------

.. autofunction:: treevalue.tree.tree.utils.filter_


union
-----------

.. autofunction:: treevalue.tree.tree.utils.union


subside
-----------

.. autofunction:: treevalue.tree.tree.utils.subside

rise
------------

.. autofunction:: treevalue.tree.tree.utils.rise


shrink
----------------

.. autofunction:: treevalue.tree.tree.utils.shrink


NO_RISE_TEMPLATE
--------------------

.. data:: treevalue.tree.tree.utils.NO_RISE_TEMPLATE

    Means no template is given to the rise function, \
    and the decorated function will automatically try \
    to match the format patterns as template.


graphics
----------------

.. autofunction:: treevalue.tree.tree.graph.graphics

Here is an example of `graphics` function. The source code is

.. literalinclude:: graphics.demo.py
    :language: python
    :linenos:

The generated graphviz source code should be

.. literalinclude:: graphics.dat.gv
    :language: text
    :linenos:

The graph should be

.. image:: graphics.dat.gv.svg
    :align: center

Also, `graphics` function can support value duplication. For if \
the value nodes are using the same object, they will be displayed \
in the same node of the generated graph, such as the source code
below

.. literalinclude:: graphics_dup_value.demo.py
    :language: python
    :linenos:

The graph of the case with `dup_value` should be

.. image:: graphics_dup_value.dat.gv.svg
    :align: center
