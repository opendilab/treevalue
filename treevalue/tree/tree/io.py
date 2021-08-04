import io
import pickle
from typing import Optional, Type, TypeVar, Union, Callable

from .tree import TreeValue, get_data_property
from ...utils import dynamic_call

_TreeType = TypeVar('_TreeType', bound=TreeValue)


def dump(t: _TreeType, file, compress: Optional[Callable] = None):
    """
    Overview:
        Dump tree value to file.

    Arguments:
        - t (:obj:`_TreeType`): Tree value object.
        - file: Target dump file.
        - compress (:obj:`Optional[Callable]`): Compress function.
    """
    compress = dynamic_call(compress or (lambda x: x))
    file.write(compress(pickle.dumps(get_data_property(t).actual())))


def dumps(t: _TreeType, compress: Optional[Callable] = None) -> bytes:
    """
    Overview:
        Dump tree value to file.

    Arguments:
        - t (:obj:`_TreeType`): Tree value object.
        - compress (:obj:`Optional[Callable]`): Compress function.

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
        - type\_ (:obj:`Type[_TreeType]`): Type of tree value, default is ``TreeValue``.
        - decompress (:obj:`Optional[Callable]`): Decompress function, default is ``None`` which means \
            do not do any decompression.

    Returns:
        - tree (:obj:`_TreeType`): Tree value object.
    """
    decompress = dynamic_call(decompress or (lambda x: x))
    return type_(pickle.loads(decompress(file.read())))


def loads(data: Union[bytes, bytearray], type_: Optional[Type[_TreeType]] = TreeValue,
          decompress: Optional[Callable] = None) -> _TreeType:
    """
    Overview:
        Load tree value object from file.

    Arguments:
        - data (:obj:`Union[bytes, bytearray]`): Binary data.
        - type\_ (:obj:`Type[_TreeType]`): Type of tree value, default is ``TreeValue``.
        - decompress (:obj:`Optional[Callable]`): Decompress function, default is ``None`` which means \
            do not do any decompression.

    Returns:
        - tree (:obj:`_TreeType`): Tree value object.
    """
    with io.BytesIO(bytes(data)) as file:
        return load(file, type_, decompress)
