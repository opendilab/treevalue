Main Idea of TreeValue
============================

Why TreeValue is designed?
----------------------------

When we build programs, especially when we need to deal \
with tree-like data structures, python-based native \
dictionaries often need to write a lot of code, and \
edit more complex and non-intuitive calculation logic.

In fact, the root cause of this problem is that the \
native python dictionary data type is a basic data \
structure that is biased towards functional \
generalization, and it does not fully meet the various \
data processing and operations based on the tree data \
structure. The TreeValue library needs to solve this problem.

For example, if we need to add all the integers of the 2 \
dictionaries together with native python, the code will be \
like below,

.. literalinclude:: native_python_demo.demo.py
    :language: python
    :linenos:

with the following output.

.. literalinclude:: native_python_demo.demo.py.txt
    :language: text
    :linenos:

Although in fact, as python coders, we may have been \
accustomed to such a native recursive writing method, \
but from the perspective of actual engineering \
construction, such a writing method is not intuitive enough:

* First of all, this way of writing has been quite \
  different from the original simple addition in terms of \
  look and feel and engineering structure. In order to \
  support dictionary-based operations, the original \
  simple addition operations have become completely \
  unrecognizable.
* Secondly, in the actual tree structure operation, \
  there may be various exception handling situations \
  (such as the missing of some key values, the \
  corresponding positions on the two trees, one is an \
  integer and the other is a child node, etc.), and if \
  you want to In the native python code, these things \
  that can often be expected with a high probability \
  are more complete and satisfactory processing, and \
  the code needs to be further complicated.
* In addition, the above code shows only operations \
  based on two trees. If we need to extend the calculation \
  itself, such as extending to operations with more than \
  two trees, or operations with less than two trees, \
  we will either continue to scale-enlarged change the \
  logic of the plus function, or use the ``reduce`` function. \
  In the former case, the above problems will be further \
  aggravated, while in the latter case, another function \
  needs to be encapsulated. No matter which kind of extension \
  method, the code will be greatly complicated, and the \
  quality for programmers will eventually be difficult to \
  guarantee.

So the ``TreeValue`` is designed to solve the above \
problems and provided sufficient secondary development \
support for developers, so that more complex and \
comprehensive applications can be developed based \
on this framework.

This is the example code to implement the functions \
of the code above.

.. literalinclude:: treevalue_demo_1.demo.py
    :language: python
    :linenos:

The result should be like below.

.. literalinclude:: treevalue_demo_1.demo.py.txt
    :language: text
    :linenos:

Besides, based on the framework provided by us, \
another way of code building can be like the following \
code.

.. literalinclude:: treevalue_demo_2.demo.py
    :language: python
    :linenos:

This code will have the same function with the codes above.

.. literalinclude:: treevalue_demo_2.demo.py.txt
    :language: text
    :linenos:

Definitions for Key Conceptions
---------------------------------

.. todo:: complete the definitions
