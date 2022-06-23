Plugins
===============

Potc support
---------------------

`Potc <https://github.com/potc-dev/potc>`_  is a package that can convert any object into executable source code.
For ``treevalue``, potc can support the source code transformation of treevalue objects through
the installation of additional plugins. So we can execute the following installation command

.. code:: shell

    pip install treevalue[potc]

After this installation, you will be able to directly convert treevalue to an object without any additional operations.
Such as

.. literalinclude:: ./potc_demo.demo.py
    :language: python
    :linenos:

The output should be

.. literalinclude:: ./potc_demo.demo.py.txt
    :language: text
    :linenos:

Also, you can use the following CLI command to get the same output results as above.

.. code:: shell

    potc export -v 'test_simple.t' -v 'test_simple.st' -v 'test_simple.r'

For further information, you can refer to

* `potc-dev/potc <https://github.com/potc-dev/potc>`_
* `potc-dev/potc-treevalue <https://github.com/potc-dev/potc-treevalue>`_
