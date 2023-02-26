# distutils:language=c++
# cython:language_level=3

cdef tuple _c_flatten_for_jax(object tv)
cdef object _c_unflatten_for_jax(tuple aux, tuple values)
cpdef void register_for_jax(object cls) except*
