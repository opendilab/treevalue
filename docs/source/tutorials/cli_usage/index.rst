Cli Usage
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
binary file with ``dump`` / ``dumps`` function define in \
module ``treevalue.tree.io``.

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

