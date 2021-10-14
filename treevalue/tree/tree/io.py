import io
import pickle
import warnings
import zlib
from typing import Optional, Type, TypeVar, Union, Callable

import dill

from .tree import TreeValue

_TreeType = TypeVar('_TreeType', bound=TreeValue)

_NO_DECOMPRESSION = 0
_NEED_DECOMPRESSION = 1


def _extract_compress_and_decompress(compress):
    if isinstance(compress, tuple):
        return compress[0], compress[1]
    elif hasattr(compress, '__call__'):
        return compress, _NEED_DECOMPRESSION
    elif compress is None:
        return (lambda x: x), _NO_DECOMPRESSION
    else:
        return getattr(compress, 'compress'), getattr(compress, 'decompress')


def dump(t: _TreeType, file, compress=None):
    """
    Overview:
        Dump tree value to file.

    Arguments:
        - t (:obj:`_TreeType`): Tree value object.
        - file: Target dump file.
        - compress: Compress object, may be compression function, \
            tuple of functions or module (``compress`` and ``decompress`` required).
    """
    compress_func, decompress_func = _extract_compress_and_decompress(compress)
    dump_data = (compress_func(dill.dumps(t._detach())),
                 zlib.compress(dill.dumps(decompress_func)))
    pickle.dump(dump_data, file)


def dumps(t: _TreeType, compress=None) -> bytes:
    """
    Overview:
        Dump tree value to file.

    Arguments:
        - t (:obj:`_TreeType`): Tree value object.
        - compress: Compress object, may be compression function, \
            tuple of functions or module (``compress`` and ``decompress`` required).

    Returns:
        - data (:obj:`bytes`): Dumped binary data.
    """
    with io.BytesIO() as file:
        dump(t, file, compress)
        return file.getvalue()


def load(file, type_: Type[_TreeType] = TreeValue, decompress: Optional[Callable] = None) -> _TreeType:
    """
    Overview:
        Load tree value object from file.

    Arguments:
        - file: Original file.
        - type\\_ (:obj:`Type[_TreeType]`): Type of tree value, default is ``TreeValue``.
        - decompress (:obj:`Optional[Callable]`): Decompress function, default is ``None`` which means \
            do not do any decompression.

    Returns:
        - tree (:obj:`_TreeType`): Tree value object.
    """
    try:
        _compressed_data, _decompress_func_data = pickle.load(file)
    except ValueError:
        raise pickle.UnpicklingError('Invalid TreeValue binary data.')

    decompress_func = dill.loads(zlib.decompress(_decompress_func_data))
    if decompress_func == _NEED_DECOMPRESSION:
        if decompress:
            decompress_func = decompress
        else:
            raise RuntimeError('Decompression function not provided but it is required.')
    elif decompress_func == _NO_DECOMPRESSION:
        if decompress:
            warnings.warn("Decompress function is not needed because the data is not compressed.")
        decompress_func = lambda x: x
    else:
        if decompress:
            warnings.warn("Decompress function is not needed "
                          "because decompression function has already been provided.")
        decompress_func = decompress_func

    return type_(dill.loads(decompress_func(_compressed_data)))


def loads(data: Union[bytes, bytearray], type_: Optional[Type[_TreeType]] = TreeValue,
          decompress: Optional[Callable] = None) -> _TreeType:
    """
    Overview:
        Load tree value object from file.

    Arguments:
        - data (:obj:`Union[bytes, bytearray]`): Binary data.
        - type\\_ (:obj:`Type[_TreeType]`): Type of tree value, default is ``TreeValue``.
        - decompress (:obj:`Optional[Callable]`): Decompress function, default is ``None`` which means \
            do not do any decompression.

    Returns:
        - tree (:obj:`_TreeType`): Tree value object.
    """
    with io.BytesIO(bytes(data)) as file:
        return load(file, type_, decompress)
