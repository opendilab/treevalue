# distutils:language=c++
# cython:language_level=3

ctypedef unsigned char boolean
ctypedef unsigned int uint

cdef void _key_validate(const char*key) except *

cdef class TreeStorage:
    cdef readonly dict map

    cpdef public void set(self, str key, object value) except *
    cpdef public object get(self, str key)
    cpdef public object get_or_default(self, str key, object default)
    cpdef public void del_(self, str key) except *
    cpdef public boolean contains(self, str key)
    cpdef public uint size(self)
    cpdef public boolean empty(self)
    cpdef public dict dump(self)
    cpdef public dict deepdump(self)
    cpdef public dict deepdumpx(self, copy_func)
    cpdef public dict jsondumpx(self, copy_func, object need_raw)
    cpdef public TreeStorage copy(self)
    cpdef public TreeStorage deepcopy(self)
    cpdef public TreeStorage deepcopyx(self, copy_func)
    cpdef public dict detach(self)
    cpdef public void copy_from(self, TreeStorage ts)
    cpdef public void deepcopy_from(self, TreeStorage ts)
    cpdef public void deepcopyx_from(self, TreeStorage ts, copy_func)

cpdef public object create_storage(dict value)
