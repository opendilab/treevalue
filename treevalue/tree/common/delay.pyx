# distutils:language=c++
# cython:language_level=3

import cython
from libcpp cimport bool

cdef class DelayedProxy:
    cpdef object value(self):
        raise NotImplementedError  # pragma: no cover

    cpdef object fvalue(self):
        return self.value()

cdef class DelayedValueProxy(DelayedProxy):
    def __cinit__(self, object func):
        self.func = func
        self.calculated = False
        self.val = None

    cpdef object value(self):
        cdef object f
        if not self.calculated:
            f = undelay(self.func, False)
            self.val = f()
            self.calculated = True

        return self.val

cdef class DelayedFuncProxy(DelayedProxy):
    def __cinit__(self, object func, tuple args, dict kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.calculated = False
        self.val = None

    cpdef object value(self):
        cdef list pas
        cdef dict pks
        cdef str key
        cdef object item
        cdef object f
        if not self.calculated:
            pas = []
            pks = {}
            f = undelay(self.func, False)
            for item in self.args:
                pas.append(undelay(item, False))
            for key, item in self.kwargs.items():
                pks[key] = undelay(item, False)

            self.val = f(*pas, **pks)
            self.calculated = True

        return self.val

cdef inline DelayedProxy _c_delayed_partial(func, args, kwargs):
    if args or kwargs:
        return DelayedFuncProxy(func, args, kwargs)
    else:
        return DelayedValueProxy(func)

def delayed_partial(func, *args, **kwargs):
    return _c_delayed_partial(func, args, kwargs)

@cython.binding(True)
cpdef inline object undelay(object p, bool is_final=True):
    if isinstance(p, DelayedProxy):
        if is_final:
            return p.fvalue()
        else:
            return p.value()
    else:
        return p
