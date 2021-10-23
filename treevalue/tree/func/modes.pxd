# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

ctypedef enum _e_tree_mode:
    STRICT
    INNER
    OUTER
    LEFT

cdef _e_tree_mode _c_load_mode(str mode) except *
cdef void _c_base_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_strict_keyset(list args, dict kwargs)
cdef void _c_strict_check(_e_tree_mode mode, object return_type,
                          bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_inner_keyset(list args, dict kwargs)
cdef void _c_inner_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_outer_keyset(list args, dict kwargs)
cdef void _c_outer_check(_e_tree_mode mode, object return_type,
                         bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_left_keyset(list args, dict kwargs)
cdef void _c_left_check(_e_tree_mode mode, object return_type,
                        bool inherit, bool allow_missing, object missing_func) except *

cdef set _c_keyset(_e_tree_mode mode, list args, dict kwargs)
cdef void _c_check(_e_tree_mode mode, object return_type,
                   bool inherit, bool allow_missing, object missing_func) except *
