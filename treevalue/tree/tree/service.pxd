# distutils:language=c++
# cython:language_level=3

# jsonify, clone, typetrans

from .tree cimport TreeValue

cdef object _keep_object(object obj)
cpdef object jsonify(TreeValue val)
cpdef TreeValue clone(TreeValue t, object copy_value= *)
cpdef TreeValue typetrans(TreeValue t, type return_type)
