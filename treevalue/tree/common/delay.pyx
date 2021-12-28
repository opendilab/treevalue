# distutils:language=c++
# cython:language_level=3

import cython

cdef class DelayedProxy:
    cpdef object value(self):
        raise NotImplementedError  # pragma: no cover

cdef class DelayedValueProxy(DelayedProxy):
    def __cinit__(self, object func):
        self.func = func
        self.calculated = False
        self.val = None

    cpdef object value(self):
        cdef object f
        if not self.calculated:
            f = unwrap_proxy(self.func)
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
            f = unwrap_proxy(self.func)
            pas = []
            pks = {}
            for item in self.args:
                pas.append(unwrap_proxy(item))
            for key, item in self.kwargs.items():
                pks[key] = unwrap_proxy(item)

            self.val = f(*pas, **pks)
            self.calculated = True

        return self.val

def delayed_partial(func, *args, **kwargs):
    if args or kwargs:
        return DelayedFuncProxy(func, args, kwargs)
    else:
        return DelayedValueProxy(func)

@cython.binding(True)
cpdef inline object unwrap_proxy(object proxy):
    if isinstance(proxy, DelayedProxy):
        return unwrap_proxy(proxy.value())
    else:
        return proxy
