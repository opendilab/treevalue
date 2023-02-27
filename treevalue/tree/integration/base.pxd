# distutils:language=c++
# cython:language_level=3

cdef tuple _c_flatten_for_integration(object tv)
cdef object _c_unflatten_for_integration(object values, tuple spec)
