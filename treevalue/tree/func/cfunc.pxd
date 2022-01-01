# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

from .modes cimport _e_tree_mode

cdef object _c_wrap_func_treelize_run(object func, list args, dict kwargs, _e_tree_mode mode, bool inherit,
                                      bool allow_missing, object missing_func, bool delayed)
cdef object _c_func_treelize_run(object func, list args, dict kwargs, _e_tree_mode mode, bool inherit,
                                 bool allow_missing, object missing_func, bool delayed)

cpdef object _d_func_treelize(object func, object mode, object return_type, bool inherit, object missing,
                              bool delayed, object subside, object rise)
cdef object _c_common_value(object item)
cdef tuple _c_missing_process(object missing)
cpdef object func_treelize(object mode= *, object return_type= *, bool inherit= *, object missing= *,
                           bool delayed= *, object subside= *, object rise= *)
