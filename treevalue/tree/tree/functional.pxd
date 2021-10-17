# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef object _single_value_process(object o)
cdef TreeStorage _c_mapping(TreeStorage st, object func, tuple path)
cdef TreeStorage _st_mapping(TreeStorage st, object func)
cpdef TreeValue mapping(TreeValue t, object func)
