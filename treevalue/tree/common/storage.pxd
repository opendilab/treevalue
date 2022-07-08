# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool
cimport cython

ctypedef unsigned char boolean
ctypedef unsigned int uint

@cython.final
cdef class TreeStorage:
    cdef readonly dict map

    cpdef public void set(self, str key, object value) except *
    cpdef public object setdefault(self, str key, object default)
    cpdef public object get(self, str key)
    cpdef public object get_or_default(self, str key, object default)
    cpdef public object pop(self, str key)
    cpdef public object pop_or_default(self, str key, object default)
    cpdef public tuple popitem(self)
    cpdef public void del_(self, str key) except *
    cpdef public void clear(self)
    cpdef public boolean contains(self, str key)
    cpdef public uint size(self)
    cpdef public boolean empty(self)
    cpdef public dict dump(self)
    cpdef public dict deepdump(self)
    cpdef public dict deepdumpx(self, copy_func)
    cpdef public dict jsondumpx(self, copy_func, bool need_raw, bool allow_delayed)
    cpdef public TreeStorage copy(self)
    cpdef public TreeStorage deepcopy(self)
    cpdef public TreeStorage deepcopyx(self, copy_func, bool allow_delayed)
    cpdef public dict detach(self)
    cpdef public void copy_from(self, TreeStorage ts)
    cpdef public void deepcopy_from(self, TreeStorage ts)
    cpdef public void deepcopyx_from(self, TreeStorage ts, copy_func, bool allow_delayed)

cpdef public object create_storage(dict value)
cdef object _c_undelay_data(dict data, object k, object v)
cdef object _c_undelay_not_none_data(dict data, object k, object v)
cdef object _c_undelay_check_data(dict data, object k, object v)
