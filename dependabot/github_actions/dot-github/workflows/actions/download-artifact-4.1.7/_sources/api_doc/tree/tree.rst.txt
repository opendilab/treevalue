treevalue.tree.tree
======================

.. py:currentmodule:: treevalue.tree.tree

.. _apidoc_tree_tree_treevalue:

TreeValue
---------------

.. autoclass:: TreeValue
    :members: __init__, __getattribute__, __setattr__, __delattr__, __contains__, __repr__, __iter__, __hash__, __eq__, _attr_extern, __len__, __bool__, __str__, __getstate__, __setstate__, get, pop, keys, values, items, __getitem__, __setitem__, __delitem__, _getitem_extern, _setitem_extern, _delitem_extern, popitem, clear, update, setdefault, __reversed__, _detach, unpack


.. _apidoc_tree_tree_delayed:

delayed
---------------

.. autofunction:: delayed


.. _apidoc_tree_tree_jsonify:

jsonify
--------------

.. autofunction:: jsonify


.. _apidoc_tree_tree_clone:

clone
-----------

.. autofunction:: clone


.. _apidoc_tree_tree_typetrans:

typetrans
------------------

.. autofunction:: typetrans


.. _apidoc_tree_tree_walk:

walk
-------------------

.. autofunction:: walk


.. _apidoc_tree_tree_flatten:

flatten
-------------------

.. autofunction:: flatten


.. _apidoc_tree_tree_flatten_values:

flatten_values
-------------------

.. autofunction:: flatten_values


.. _apidoc_tree_tree_flatten_keys:

flatten_keys
-------------------

.. autofunction:: flatten_keys


.. _apidoc_tree_tree_unflatten:

unflatten
-------------------

.. autofunction:: unflatten


.. _apidoc_tree_tree_mapping:

mapping
--------------

.. autofunction:: mapping


.. _apidoc_tree_tree_mask:

mask
-------------------

.. autofunction:: mask


.. _apidoc_tree_tree_filter:

filter\_
----------------------

.. autofunction:: filter_


.. _apidoc_tree_tree_union:

union
-----------

.. autofunction:: union


.. _apidoc_tree_tree_subside:

subside
-----------

.. autofunction:: subside


.. _apidoc_tree_tree_rise:

rise
------------

.. autofunction:: rise


.. _apidoc_tree_tree_reduce:

reduce\_
----------------

.. autofunction:: reduce_


.. _apidoc_tree_tree_graphics:

graphics
----------------

.. autofunction:: graphics

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

The return value's type of function ``graphics`` is \
class ``graphviz.dot.Digraph``, from the opensource \
library ``graphviz``, for further information of \
this project and ``graphviz.dot.Digraph``'s usage, \
take a look at:

* `Official site of Graphviz <https://graphviz.org/>`_.
* `User Guide of Graphviz <https://graphviz.readthedocs.io/en/stable/manual.html#formats>`_.
* `API Reference of Graphviz <https://graphviz.readthedocs.io/en/stable/api.html>`_.


.. _apidoc_tree_tree_dump:

dump
-------------

.. autofunction:: dump


.. _apidoc_tree_tree_dumps:

dumps
-------------

.. autofunction:: dumps


.. _apidoc_tree_tree_load:

load
-------------

.. autofunction:: load


.. _apidoc_tree_tree_loads:

loads
-------------

.. autofunction:: loads


register_dict_type
----------------------------

.. autofunction:: register_dict_type



