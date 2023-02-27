# distutils:language=c++
# cython:language_level=3

cdef tuple _c_flatten_for_torch(object tv)
cdef object _c_unflatten_for_torch(list values, tuple context)
cpdef void register_for_torch(object cls) except*