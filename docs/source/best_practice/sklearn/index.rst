Apply into Scikit-Learn
===========================

Actually, ``TreeValue`` can be used in practice with not only ``numpy`` or ``torch`` library, such as ``scikit-learn``.
In the following part, a demo of PCA to tree-structured arrays will be shown.

In the field of traditional machine learning, PCA (Principal Component Analysis) is often used to preprocess data,
by normalizing the data range, and trying to reduce the dimensionality of the data, so as to reduce the complexity
of the input data and improve machine learning's efficiency and quality. Just as the following image

.. figure:: heading_of_pca.jpg
    :alt: PCA Principle

    PCA in a nutshell. Source: Lavrenko and Sutton 2011, slide 13.

In the scikit-learn library, the PCA class is provided to support this function, and the function ``fit_transform``
can be used to simplify the data. For a set of ``np.array`` format data that presents a tree structure,
we can implement the operation support for the tree structure by quickly wrapping the function ``fit_transform``.
The specific code is as follows

.. literalinclude:: sklearn.demo.py
    :language: python
    :linenos:

The output should be

.. literalinclude:: sklearn.demo.py.txt
    :language: text
    :linenos:

For further information, see the links below:

* `Official documentation of PCA in scikit-learn <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html?highlight=pca#sklearn.decomposition.PCA>`_
* `Details of PCA <https://devopedia.org/principal-component-analysis>`_

