# distutils:language=c++
# cython:language_level=3

import cython
from libcpp cimport bool

cdef class DelayedProxy:
    """
    Overview:
        Base class of all the delayed proxy class.
    """
    cpdef object value(self):
        r"""
        Overview:
            Get value of the delayed proxy.
            Should make sure the result is cached.
            Can be accessed in :func:`treevalue.tree.common.undelay` when ``is_final`` is ``False``.

        Returns:
            - value (:obj:`object`): Calculation result.
        """
        raise NotImplementedError  # pragma: no cover

    cpdef object fvalue(self):
        r"""
        Overview:
            Get value of the delayed proxy.
            Can be accessed in :func:`treevalue.tree.common.undelay` when ``is_final`` is ``True``.

        Returns:
            - value (:obj:`object`): Calculation result.
        """
        return self.value()

cdef class DelayedValueProxy(DelayedProxy):
    """
    Overview:
        Simple function delayed proxy.
    """
    def __cinit__(self, object func):
        """
        Overview:
            Constructor of class :class:`treevalue.tree.common.DelayedValueProxy`.

        Arguments:
            - func (:obj:`object`): Function to be called, which can be called without arguments. \
                Delayed proxy is supported.
        """
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
    """
    Overview:
        Simple function delayed proxy.
    """
    def __cinit__(self, object func, tuple args, dict kwargs):
        """
        Overview:
            Constructor of class :class:`treevalue.tree.common.DelayedFuncProxy`.

        Arguments:
            - func (:obj:`object`): Function to be called, which can be called with given arguments. \
                Delayed proxy is supported.
            - args (:obj:`tuple`): Positional arguments to be used, delayed proxy is supported.
            - kwargs (:obj:`dict`): Key-word arguments to be used, delayed proxy is supported.
        """
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

@cython.binding(True)
def delayed_partial(func, *args, **kwargs):
    """
    Overview:
        Build a delayed partial object.
        Similar to :func:`functools.partial`.

    Returns:
        - delayed: Delayed object.
    """
    return _c_delayed_partial(func, args, kwargs)

@cython.binding(True)
cpdef inline object undelay(object p, bool is_final=True):
    r"""
    Overview:
        Get the value of a given object, it can be a delayed proxy, a simple object or \
            a nested delayed proxy.
    
    Arguments:
        - p (:obj:`object`): Given object to be undelay.
        - is_final (:obj:`bool`): Is final value getting or not, default is ``True``. 

    Returns:
        - value (:obj:`object): Actual value of the given ``p``.
    """
    if isinstance(p, DelayedProxy):
        if is_final:
            return p.fvalue()
        else:
            return p.value()
    else:
        return p
