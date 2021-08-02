Main Idea of TreeValue
============================

.. _tutorials_mainidea_why:

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


.. _tutorials_mainidea_definition:

Definitions for Key Conceptions
---------------------------------

In this section, the following key conceptions will be \
introduced:

* TreeValue
* Tree Calculation
* Tree Function Wrapper


.. _tutorials_mainidea_definition_treevalue:

TreeValue
~~~~~~~~~~~~~~~~~~~~

TreeValue is a data structure which is based on \
tree structure. Nested features of tree structure \
are natively supported in TreeValue. In this project, \
**TreeValue is the basic calculation unit of any \
operations**.

From a data structure perspective, TreeValue is a \
rooted, directed tree, and their nodes can be divided \
into two categories:

* Non-leaf node, represents the subtree structure.
* Leaf node, which stores the value.

Also, each edge of the tree has one string key which length \
is no less than ``1``, and all edges from the same parent \
node have different keys with each other. The following \
graph shows a simple example, the TreeValue ``t`` is \
a TreeValue instance, for the diamond-shaped node is the \
root node, the circle-shaped node is the non-leaf nodes \
and the rectangle-shaped node is the leaf nodes with \
their values.

.. image:: treevalue_demo.gv.svg
    :align: center


.. _tutorials_mainidea_definition_treelize:

Treelize
~~~~~~~~~~~~~~~~~~~~~~

Base on the definition of TreeValue, the calculation based \
on it is named `Tree Calculation`.

Usually, the native calculation, operations in python \
are all able to be abstracted to functions, for the \
values can be mapped as the arguments of the function, \
and the function's return value is the calculation's \
result. For example, native ``+`` operator can be transformed \
to ``__add__`` function (actually it has already been \
define in ``operators`` module and can be imported in \
your code), the expression :math:`1 + 2 = 3` can be \
transformed to function-based expression of \
:math:`\_\_add\_\_(1, 2) = 3`. In mathematical form, \
the transformed functions can be tagged as :math:`f`.

.. image:: treelize_demo.gv.svg
    :align: center

And if we need to expand these function to support the \
similar calculation on the TreeValue instances (just like \
the graph shows above), we will need to expand the \
function :math:`f` to a new tree-supported function \
which is named :math:`f_T`. For example, the ``__add__`` \
function for native integers can be seen as function \
:math:`f`, while the ``_add__`` function on the TreeValue \
in the example above is the expanded function :math:`f_T`.

.. note::

    Actually, the function :math:`f_T` will not change \
    any mathematical properties when all the arguments \
    are native values. Expressed in symbolic expression \
    is (all the :math:`a_i \left(0 \leq i \leq n\right)`, \
    satisfies that :math:`a_i` is a native value).

    .. math::

        \forall \left\{ a_i \right\} \left( 0 \leq i \leq n\right), f_T\left(a_0, a_1, \cdots, a_n\right) = f\left(a_0, a_1, \cdots, a_n\right)

    Based on this mathematical property, treelize \
    operation to the native functions will not change its \
    original property, when you are using it as a \
    native function, you will feel native special than usual.

So we can define this kind of mappings from \
function :math:`f` to :math:`f_T` as \
mapping :math:`T`, so the treelize process can be \
expressed in the following symbolic form:

.. math::

    f_T = T\left( f \right)

Based on this, the actual tree-based calculation's \
process can be expressed as:

.. math::

    f_T\left(a_0, a_1, \cdots, a_n\right) \
    = T\left(f\right)\left(a_0, a_1, \cdots, a_n\right)

The TreeValue and treelize functions are the core \
features that supported this project, and all of the \
calculation. The TreeValue is implemented as class \
``TreeValue`` in this project (the extended one is \
called ``FastTreeValue``), and treelize is implemented \
as function ``func_treelize`` in this project (the treelize \
function for instance methods and class methods are \
called ``method_treelize`` and ``classmethod_treelize``.
