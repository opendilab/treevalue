# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

ctypedef enum _e_tree_mode:
    STRICT
    INNER
    OUTER
    LEFT

cdef _e_tree_mode _c_load_mode(object mode) except *
cdef void _c_base_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_strict_keyset(tuple args, dict kwargs)
cdef void _c_strict_check(_e_tree_mode mode, object return_type,
                          bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_inner_keyset(tuple args, dict kwargs)
cdef void _c_inner_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_outer_keyset(tuple args, dict kwargs)
cdef void _c_outer_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_left_keyset(tuple args, dict kwargs)
cdef void _c_left_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_keyset(_e_tree_mode mode, tuple args, dict kwargs)
cdef void _c_check(_e_tree_mode mode, object return_type,
                   bool inherit, bool allow_missing, object missing_func) except *
