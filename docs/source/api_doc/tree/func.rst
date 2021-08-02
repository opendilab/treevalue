treevalue.tree.func
=============================

.. _apidoc_tree_func_functreelize:

func_treelize
--------------------

.. autofunction:: treevalue.tree.func.func_treelize


.. _apidoc_tree_func_treeclass:

tree_class
----------------------

.. autofunction:: treevalue.tree.func.tree_class


.. _apidoc_tree_func_methodtreelize:

method_treelize
--------------------

.. autofunction:: treevalue.tree.func.method_treelize


.. _apidoc_tree_func_utilsclass:

utils_class
----------------------

.. autofunction:: treevalue.tree.func.utils_class


.. _apidoc_tree_func_classmethodtreelize:

classmethod_treelize
--------------------

.. autofunction:: treevalue.tree.func.classmethod_treelize


TreeMode
--------------

.. autoenum:: treevalue.tree.func.TreeMode
    :members: loads

MISSING_NOT_ALLOW
-------------------------

.. data:: treevalue.tree.func.MISSING_NOT_ALLOW

    Default value of the ``missing`` arguments \
    of ``func_treelize``, ``method_treelize`` and \
    ``classmethod_treelize``, \
    which means missing is not allowed \
    (raise ``KeyError`` when missing is detected).

AUTO_DETECT_RETURN_TYPE
----------------------------

.. data:: treevalue.tree.func.AUTO_DETECT_RETURN_TYPE

    Default value of the ``return_type`` arguments \
    of ``method_treelize`` and ``classmethod_treelize``, \
    which means return type will be auto configured to
    the current class.
