treevalue.tree.tree
======================

.. _apidoc_tree_tree_treevalue:

TreeValue
---------------

.. autoclass:: treevalue.tree.tree.tree.TreeValue
    :members: __init__, __getattr__, __setattr__, __delattr__, __contains__, __repr__, __iter__, __hash__, __eq__, _attr_extern, __len__, __bool__, __str__, __getstate__, __setstate__


.. _apidoc_tree_tree_jsonify:

jsonify
--------------

.. autofunction:: treevalue.tree.tree.utils.jsonify


.. _apidoc_tree_tree_view:

view
----------

.. autofunction:: treevalue.tree.tree.utils.view


.. _apidoc_tree_tree_clone:

clone
-----------

.. autofunction:: treevalue.tree.tree.utils.clone


.. _apidoc_tree_tree_typetrans:

typetrans
------------------

.. autofunction:: treevalue.tree.tree.utils.typetrans


.. _apidoc_tree_tree_mapping:

mapping
--------------

.. autofunction:: treevalue.tree.tree.utils.mapping


.. _apidoc_tree_tree_mask:

mask
-------------------

.. autofunction:: treevalue.tree.tree.utils.mask


.. _apidoc_tree_tree_filter:

filter\_
----------------------

.. autofunction:: treevalue.tree.tree.utils.filter_


.. _apidoc_tree_tree_union:

union
-----------

.. autofunction:: treevalue.tree.tree.utils.union


.. _apidoc_tree_tree_subside:

subside
-----------

.. autofunction:: treevalue.tree.tree.utils.subside


.. _apidoc_tree_tree_rise:

rise
------------

.. autofunction:: treevalue.tree.tree.utils.rise


.. _apidoc_tree_tree_reduce:

reduce\_
----------------

.. autofunction:: treevalue.tree.tree.utils.reduce_


NO_RISE_TEMPLATE
--------------------

.. data:: treevalue.tree.tree.utils.NO_RISE_TEMPLATE

    Means no template is given to the rise function, \
    and the decorated function will automatically try \
    to match the format patterns as template.


.. _apidoc_tree_tree_graphics:

graphics
----------------

.. autofunction:: treevalue.tree.tree.graph.graphics

Here is an example of ``graphics`` function. The source code is

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

Also, ``graphics`` function can support value duplication. For if \
the value nodes are using the same object, they will be displayed \
in the same node of the generated graph, such as the source code
below

.. literalinclude:: graphics_dup_value.demo.py
    :language: python
    :linenos:

The graph of the case with ``dup_value`` should be

.. image:: graphics_dup_value.dat.gv.svg
    :align: center
