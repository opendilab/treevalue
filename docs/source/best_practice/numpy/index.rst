Apply into Numpy
======================

In following parts, we will show some demos about how to use ``TreeValue`` in practice.

For example, now we have a group of structed data in python-dict type, we want to do different operations on differnent key-value pairs inplace, 
get some statistics such as mean value and task some slices.


In normal cases, we need to unroll multiple ``for-loop`` and ``if-else`` to implement cooresponding operations on each values, and declare additional
temporal variables to save result. All the mentioned contents are executed serially, like the next code examples:

.. literalinclude:: without_treevalue.py
    :language: python
    :linenos:

However, with the help of ``TreeValue``, all the contents mentioned above can be implemented gracefully and efficiently. Users only need to ``func_treelize`` the primitive
numpy functions and pack data with ``FastTreeValue``, then execute desired operations just like using standard numpy array.

.. literalinclude:: with_treevalue.py
    :language: python
    :linenos:

And we can run these two demos for comparison:

.. literalinclude:: numpy.demo.py
    :language: python
    :linenos:

The final output should be the text below, and all the assertions can be passed.

.. literalinclude:: numpy.demo.py.txt
    :language: text
    :linenos:

In this case, we can see that the ``TreeValue`` can be properly applied into the ``numpy`` library.
The tree-structured matrix calculation can be easily built with ``TreeValue`` like using standard numpy array.

Both the simplicity of logic structure and execution efficiency can be improve a lot.

**And Last but not least, the only thing you need to do is to wrap the functions in Numpy library, and then use it painlessly like the primitive numpy.**
