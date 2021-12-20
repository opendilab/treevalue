CLI Usage
======================

From treevalue version ``0.1.0``, simple CLI (Command \
Line Interface) is provided to simplify some operations and \
optimize the use experience. This page will introduce \
the usage of cli.

Version Display
-------------------------------

You can see the version information with the following \
command typing into the terminal:

.. literalinclude:: version_demo.demo.sh
    :language: shell
    :linenos:

The output should be

.. literalinclude:: version_demo.demo.sh.txt
    :language: text
    :linenos:

.. note::
    You can check if the treevalue package is installed \
    properly with this command line since version ``0.1.0``.


Help Information Display
-------------------------------

You can see the help information of this cli by the \
following command line:

.. literalinclude:: help_demo.demo.sh
    :language: shell
    :linenos:

The output should be

.. literalinclude:: help_demo.demo.sh.txt
    :language: text
    :linenos:

There are several sub commands in ``treevalue`` cli, and they \
will be introduced in the following sections.

Exporting Trees to Binary
---------------------------------

First, let's see what is in ``treevalue export`` sub command.

.. literalinclude:: export_help_demo.demo.sh.txt
    :language: text
    :linenos:

In this sub command, we can export a tree value object to \
binary file with :ref:`apidoc_tree_tree_dump`, \
:ref:`apidoc_tree_tree_dumps` function define in \
module :doc:`../../api_doc/tree/tree`.

.. note::

    For further information, take a look at:

    * API Documentation of :ref:`apidoc_tree_tree_dump`.
    * API Documentation of :ref:`apidoc_tree_tree_dumps`.

Export One Tree
~~~~~~~~~~~~~~~~~~~~~~~

Before exporting, we prepare a python source code \
file ``tree_demo.py`` with the content of

.. literalinclude:: tree_demo.py
    :language: python
    :linenos:

And then we can to export ``t1`` to binary file, like this

.. literalinclude:: export_demo_1.demo.sh
    :language: shell
    :linenos:

A binary file named ``export_t1.dat.btv`` will be exported.

.. literalinclude:: export_demo_1.demo.sh.txt
    :language: text
    :linenos:

The binary file is exported with \
the :ref:`apidoc_tree_tree_dump` function, and the \
compression algorithm used is the default \
one ``zlib``.


Export Multiple Trees Once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can export multiple trees at one time with the following \
command

.. literalinclude:: export_demo_2.demo.sh
    :language: shell
    :linenos:

Three binary files named ``me_t1.dat.btv``, \
``me_t2.dat.btv`` and ``me_t3.dat.btv`` will be exported.

.. literalinclude:: export_demo_2.demo.sh.txt
    :language: text
    :linenos:


.. _cli_usage_export:

Export Tree with Compression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can assign compression algorithm by the ``-c`` option, \
like this

.. literalinclude:: export_demo_3.demo.sh
    :language: shell
    :linenos:

The binary file named ``compress_t1.dat.btv`` will be exported \
with the ``gzip`` compression, and will be able to be loaded \
with :ref:`treevalue graph cli <cli_usage_graph>` \
and :ref:`apidoc_tree_tree_load` function without \
the assignment of decompression algorithm.

.. literalinclude:: export_demo_3.demo.sh.txt
    :language: text
    :linenos:


I DO NOT NEED COMPRESSION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not need compression due to the reasons like \
the time scarcity, you can easily disable the compression.

.. literalinclude:: export_demo_4.demo.sh
    :language: shell
    :linenos:

The dumped binary file ``raw_t1.dat.btv`` will not be \
compressed due to the ``-r`` option.

.. literalinclude:: export_demo_4.demo.sh.txt
    :language: text
    :linenos:

.. note::

    You may feel puzzled that why the size of the \
    uncompressed version is even smaller \
    than the compressed version. The reason is easy, when the \
    :ref:`apidoc_tree_tree_load` and :ref:`apidoc_tree_tree_loads` \
    functions are called, it will crack the decompression \
    function from the binary data, which means the decompression \
    function is actually stored in binary data.

    Because of this principle, when the original data is not \
    big enough, the compressed version may be a little bit \
    bigger than the uncompressed one. But when the original \
    data is huge, the compression will show its advantage, \
    like this source file ``large_tree_demo.py``.

    .. literalinclude:: large_tree_demo.py
        :language: python
        :linenos:

    When we try to dump the ``t1`` in it, the result will be \
    satisfactory.

    .. literalinclude:: export_demo_5.demo.sh
        :language: python
        :linenos:

    .. literalinclude:: export_demo_5.demo.sh.txt
        :language: text
        :linenos:


All the binary file generated in this section (\
:ref:`cli_usage_export`) can:

* Be loaded by function :ref:`apidoc_tree_tree_load` \
  and :ref:`apidoc_tree_tree_loads` in python source code.
* Be loaded by :ref:`treevalue graph cli <cli_usage_graph>` \
  and generate its graph.


.. _cli_usage_graph:

Generate Graph from Trees
---------------------------------

First, let's see what is in ``treevalue graph`` sub command.

.. literalinclude:: graph_help_demo.demo.sh.txt
    :language: text
    :linenos:

In this sub command, we can draw a tree value object to \
a graph formatted ``png``, ``svg`` or just ``gv`` code \
with :ref:`apidoc_tree_tree_graphics` function define in \
module :doc:`../../api_doc/tree/tree`. Also, the dumped \
binary trees can be imported and then drawn to graphs.

.. note::

    For further information, take a look at:

    * API Documentation of :ref:`apidoc_tree_tree_load`.
    * API Documentation of :ref:`apidoc_tree_tree_loads`.
    * API Documentation of :ref:`apidoc_tree_tree_graphics`.

Draw One Graph For One Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before drawing the first graph, we prepare the ``tree_demo.py`` \
mentioned in :ref:`cli_usage_export`.

.. literalinclude:: tree_demo.py
    :language: python
    :linenos:

We can draw the graph of ``t1`` with the following command

.. literalinclude:: graph_demo_1.demo.sh
    :language: shell
    :linenos:

The dumped graph ``only_t1.dat.svg`` should be like this

.. image:: only_t1.dat.svg
    :align: center


Draw One Graph For Multiple Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actually we can put several trees into one graph, just like \
the following command

.. literalinclude:: graph_demo_2.demo.sh
    :language: shell
    :linenos:

The dumped graph ``t1_t2_t3.dat.svg`` should contains 3 trees, \
like this

.. image:: t1_t2_t3.dat.svg
    :align: center

Sometime, the trees will share some common nodes (with the same \
``Tree`` object id), this relation will also be displayed in \
graph. In another python script ``node_share_demo.py``

.. literalinclude:: node_share_demo.py
    :language: python
    :linenos:

The dumped graph ``shared_nodes.dat.svg`` should be like

.. image:: shared_nodes.dat.svg
    :align: center

The arrow from ``nt3`` named ``first`` is pointed to ``nt1``, \
the arrow named ``another`` is pointed to ``nt1.x``, and so on.


Graph with Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometime we need to assign the title of the dumped graph, \
or you may think that the white background look prominent in \
the grey page background. So you can dump the graph like this

.. literalinclude:: graph_demo_4.demo.sh
    :language: shell
    :linenos:

The dumped graph ``shared_nodes_with_cfg.dat.svg`` should be \
like this

.. image:: shared_nodes_with_cfg.dat.svg
    :align: center

We can see the title and the background color is changed \
because of the ``-T`` and ``-c`` command. The transparent \
background looks better than the ``shared_nodes.dat.svg`` \
in the grey page background.


Graph of Different Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not need svg format, you can dump it to png format \
like this

.. literalinclude:: graph_demo_5.demo.sh
    :language: python
    :linenos:

The dumped graph ``shared_nodes.dat.png`` should be like this, \
its format is ``png``.

.. image:: shared_nodes.dat.png
    :align: center

Besides, if the graphviz code (``gv`` format) is just all \
what you need, you can dump the ``gv`` source code with the \
following command line.

.. literalinclude:: graph_demo_6.demo.sh
    :language: python
    :linenos:

The dumped source code ``shared_nodes.dat.gv`` should be like \
this

.. literalinclude:: shared_nodes.dat.gv
    :language: graphviz
    :linenos:

Or if you need to put it to the ``stdout``, you can do like this

.. literalinclude:: graph_demo_7.demo.sh
    :language: python
    :linenos:

The output in ``stdout`` should almost the same like the \
source code file ``shared_nodes.dat.gv``.

.. note::
    When ``-O`` option is used, the ``-o`` will be ignored.

Reuse the Value Nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, the values in the trees' nodes is the same object \
(using the same memory id). So it's better to put them together \
in the dumped graph.

For example, in the python code file ``share_demo.py``

.. literalinclude:: share_demo.py
    :language: python
    :linenos:

You can run the following command

.. literalinclude:: graph_demo_8.demo.sh
    :language: shell
    :linenos:

The dumped graph ``no_shared_values.dat.svg`` should be like \
this, all the value nodes are separated in the default \
options.

.. image:: no_shared_values.dat.svg
    :align: center

We can solve this problem by adding ``-D`` option in the command, \
which means duplicate all the value nodes.

.. literalinclude:: graph_demo_9.demo.sh
    :language: shell
    :linenos:

In the dumped graph ``shared_all_values.dat.svg``, all the value \
nodes with the same id are put together.

.. image:: shared_all_values.dat.svg
    :align: center

.. note::
    When ``-D`` is used, all the values in leaf node with the \
    same id will share exactly one leaf node in the dumped \
    graph.

    But actually in python, most of the basic data \
    types are immutable, which means all the ``1`` in python \
    code are actually the same object, for their ids are \
    the same. So in the image ``shared_all_values.dat.svg``, \
    even the leaf node ``1`` are shared.

    This phenomenon may reduce the intuitiveness of the \
    image in many cases. Please notice this when you are \
    deciding to use ``-D`` option.

Because of the problem mentioned in the note above, in most of \
the cases, it's a better idea to use ``-d`` option to assign \
which types should be duplicated and which should not. Like the \
example below.

.. literalinclude:: graph_demo_10.demo.sh
    :language: shell
    :linenos:

The dumped graph ``shared_values.dat.svg`` should be like this, \
the ``1`` is not duplicated any more, but ``list`` \
and ``np.ndarray`` will be duplicated.

.. image:: shared_values.dat.svg
    :align: center


