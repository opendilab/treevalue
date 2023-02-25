# distutils:language=c++
# cython:language_level=3

import itertools
from functools import wraps, partial
from threading import Lock

import cython

from .structural cimport _c_create_sequence_with_type
from .tree cimport TreeValue
from ..common.storage cimport TreeStorage, create_storage

cdef inline tuple _c_extract_structure(object obj):
    cdef TreeStorage storage
    cdef object type_
    cdef object key, item, _r_pattern, _r_value
    cdef list _l_patterns, _l_values
    cdef dict _d_patterns, _d_values

    if isinstance(obj, TreeValue):
        storage = obj._detach()
        return type(obj), storage.dump()

    elif isinstance(obj, (list, tuple)):
        type_ = type(obj)
        _l_patterns = []
        _l_values = []
        for item in obj:
            _r_pattern, _r_value = _c_extract_structure(item)
            _l_patterns.append(_r_pattern)
            _l_values.append(_r_value)

        return _c_create_sequence_with_type(type_, _l_patterns), \
            _c_create_sequence_with_type(type_, _l_values)

    elif isinstance(obj, dict):
        type_ = type(obj)
        _d_patterns = {}
        _d_values = {}
        for key, item in obj.items():
            _r_pattern, _r_value = _c_extract_structure(item)
            _d_patterns[key] = _r_pattern
            _d_values[key] = _r_value

        return type_(_d_patterns), type_(_d_values)

    else:
        return None, obj

cdef inline object _c_rebuild_structure(object pattern, object obj):
    cdef TreeStorage storage
    cdef object key, pattern_item, value_item
    cdef list _l_values
    cdef dict _d_values

    if pattern is None:
        return obj

    elif isinstance(pattern, type) and issubclass(pattern, TreeValue):
        storage = create_storage(obj)
        return pattern(storage)

    elif isinstance(pattern, (list, tuple)):
        _l_values = []
        for pattern_item, value_item in zip(pattern, obj):
            _l_values.append(_c_rebuild_structure(pattern_item, value_item))
        return _c_create_sequence_with_type(type(pattern), _l_values)

    elif isinstance(pattern, dict):
        _d_values = {}
        for key, pattern_item in pattern.items():
            _d_values[key] = _c_rebuild_structure(pattern_item, obj[key])
        return type(pattern)(_d_values)

    else:
        raise RuntimeError(
            f'Unknown pattern for rebuild, some unexpected error may occurred - {pattern!r}.')  # pragma: no cover

_MAX_INT = (1 << 31) - 1
PENETRATE_SESSIONID_ARGNAME = '__penetrate_session_id'

@cython.binding(True)
def penetrate(decorator, **kwargs):
    """
    Overview:
        Penetrate `TreeValue` object through decorated function, such as `jax.jit`.

    :param decorator: Original decorator
    :param kwargs: Other keyword arguments, will be passed into `decorator`.

    .. note::
        :func:`penetrate` can be used on `jax.jit`.

        >>> import jax
        >>> import numpy as np
        >>> from treevalue import FastTreeValue, PENETRATE_SESSIONID_ARGNAME, penetrate
        >>>
        >>> @penetrate(jax.jit, static_argnames=PENETRATE_SESSIONID_ARGNAME)
        ... def double(x):
        ...     return x * 2
        >>>
        >>> t = FastTreeValue({
        ...     'a': np.random.randint(0, 10, (2, 3)),
        ...     'b': {
        ...         'x': 233,
        ...         'y': np.random.randn(2, 3)
        ...     }
        ... })
        >>>
        >>> t
        <FastTreeValue 0x7ff8facde8d0>
        ├── 'a' --> array([[0, 0, 7],
        │                  [9, 6, 4]])
        └── 'b' --> <FastTreeValue 0x7ff8deb3d110>
            ├── 'x' --> 233
            └── 'y' --> array([[ 0.86424466,  0.62416234, -0.76929206],
                               [ 1.16229066, -0.28098265,  0.1849025 ]])
        >>> double(t)
        WARNING:jax._src.lib.xla_bridge:No GPU/TPU found, falling back to CPU. (Set TF_CPP_MIN_LOG_LEVEL=0 and rerun for more info.)
        <FastTreeValue 0x7ff8dea57410>
        ├── 'a' --> DeviceArray([[ 0,  0, 14],
        │                        [18, 12,  8]], dtype=int32)
        └── 'b' --> <FastTreeValue 0x7ff8dea57350>
            ├── 'x' --> DeviceArray(466, dtype=int32, weak_type=True)
            └── 'y' --> DeviceArray([[ 1.7284893,  1.2483246, -1.5385841],
                                     [ 2.3245814, -0.5619653,  0.369805 ]], dtype=float32)
        >>> double(t + 1)
        <FastTreeValue 0x7ff8dea57810>
        ├── 'a' --> DeviceArray([[ 2,  2, 16],
        │                        [20, 14, 10]], dtype=int32)
        └── 'b' --> <FastTreeValue 0x7ff8dea57890>
            ├── 'x' --> DeviceArray(468, dtype=int32, weak_type=True)
            └── 'y' --> DeviceArray([[3.7284894 , 3.2483246 , 0.46141586],
                                     [4.324581  , 1.4380347 , 2.369805  ]], dtype=float32)
    """
    session_pool = {}
    counter = itertools.count()
    lock = Lock()

    def _alloc_session_id():
        with lock:
            while True:
                _session_id = next(counter) % _MAX_INT
                if _session_id not in session_pool:
                    session_pool[_session_id] = {}
                    return _session_id

    @wraps(decorator)
    def _new_decorator(func):
        @partial(decorator, **kwargs)
        def _post_func(*args_, __penetrate_session_id, **kwargs_):
            if not isinstance(__penetrate_session_id, int) or __penetrate_session_id not in session_pool:
                raise RuntimeError(
                    f'Session id argument {PENETRATE_SESSIONID_ARGNAME!r} is polluted during decoration of {decorator!r}. \n'
                    f'Please ensure that this parameter remains unchanged during the pass. \n'
                    f'If you are using jax.jit, you may put {PENETRATE_SESSIONID_ARGNAME!r} into \'static_argnames\', '
                    f'like @penetrate(jax.jit, static_argnames=({PENETRATE_SESSIONID_ARGNAME!r},)), onto your function\'s definition.')
            _input_pattern = session_pool[__penetrate_session_id]['input_pattern']
            _actual_args, _actual_kwargs = _c_rebuild_structure(_input_pattern, (args_, kwargs_))

            retval = func(*_actual_args, **_actual_kwargs)
            _output_pattern, _actual_retval = _c_extract_structure(retval)
            session_pool[__penetrate_session_id]['output_pattern'] = _output_pattern
            return _actual_retval

        @wraps(func)
        def _new_func(*args_, **kwargs_):
            _session_id = _alloc_session_id()
            try:
                _input_pattern, (_new_args, _new_kwargs) = _c_extract_structure((args_, kwargs_))
                session_pool[_session_id]['input_pattern'] = _input_pattern
                retval = _post_func(*_new_args, __penetrate_session_id=_session_id, **_new_kwargs)
                _output_pattern = session_pool[_session_id]['output_pattern']
            finally:
                del session_pool[_session_id]

            return _c_rebuild_structure(_output_pattern, retval)

        return _new_func

    return _new_decorator
