Apply into Numpy
======================



This is the code implement without ``TreeValue``, named `without_treevalue.py`.

.. literalinclude:: without_treevalue.py
    :language: python
    :linenos:

This is the code implement with the usage of ``TreeValue``, named `with_treevalue.py`.

.. literalinclude:: with_treevalue.py
    :language: python
    :linenos:

And this is the running dispatch of this demo.

.. literalinclude:: numpy.demo.py
    :language: python
    :linenos:

The final output should be the text below, and all the assertions can be passed.

.. literalinclude:: numpy.demo.py.txt
    :language: text
    :linenos:

In this case, we can see that the ``TreeValue`` can be properly applied onto the ``numpy`` library.
The tree-structured matrix calculation can be easily built with ``TreeValue``,
and the service logic structure are much more clear than the nested-dict-based
code.
Because of the convenient of ``TreeValue``, refactor operation can be
processed mush faster than the primitive code as well.
**Only what you need to do, is to wrap the functions in Numpy library, and then use it painlessly, like when you use primitive Numpy.**
