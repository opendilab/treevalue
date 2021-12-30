# distutils:language=c++
# cython:language_level=3

# mapping, filter_, mask, reduce_

from libcpp cimport bool

from .tree cimport TreeValue
from ..common.storage cimport TreeStorage

cdef object _c_no_arg(object func, object v, object p)
cdef object _c_one_arg(object func, object v, object p)
cdef object _c_two_args(object func, object v, object p)
cdef object _c_wrap_mapping_func(object func)
cdef object _c_delayed_mapping(object so, object func, tuple path, bool delayed)
cdef TreeStorage _c_mapping(TreeStorage st, object func, tuple path, bool delayed)
cpdef TreeValue mapping(TreeValue tree, object func, bool delayed= *)
cdef TreeStorage _c_filter_(TreeStorage st, object func, tuple path, bool remove_empty)
cpdef TreeValue filter_(TreeValue tree, object func, bool remove_empty= *)
cdef object _c_mask(TreeStorage st, object sm, tuple path, bool remove_empty)
cpdef TreeValue mask(TreeValue tree, object mask_, bool remove_empty= *)
cdef object _c_reduce(TreeStorage st, object func, tuple path, object return_type)
cpdef object reduce_(TreeValue tree, object func)
