# distutils:language=c++
# cython:language_level=3

# flatten, unflatten

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef void _c_flatten(TreeStorage st, tuple path, list res) except *
cpdef list flatten(TreeValue tree)

cdef void _c_flatten_values(TreeStorage st, list res) except *
cpdef list flatten_values(TreeValue tree)

cdef void _c_flatten_keys(TreeStorage st, tuple path, list res) except *
cpdef list flatten_keys(TreeValue tree)

cdef TreeStorage _c_unflatten(object pairs)
cpdef TreeValue unflatten(object pairs, object return_type= *)
