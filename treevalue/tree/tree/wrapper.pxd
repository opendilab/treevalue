# distutils:language=c++
# cython:language_level=3

# flatten, unflatten


cdef tuple _c_extract_structure(object obj)
cdef object _c_rebuild_structure(object pattern, object obj)

