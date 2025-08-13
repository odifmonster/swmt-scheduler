from typing import TypeVar, Generic, Unpack, Hashable
from app.groups.data import Data

_T = TypeVar('_T', bound=Hashable)
_U = TypeVar('_U', bound=Hashable)

class Grouped(Generic[_T, _U]):
    """
    A generic class for Grouped objects. These are mapping-like objects that allow multi-indexing
    and organize their contents according to the property names passed into the initializer. The
    first type parameter is the id type of the data, the second is the type of the outermost axis
    keys. Do not instantiate directly.
    """
    def __init__(self, *args: Unpack[tuple[str, ...]], **kwargs) -> None:
        """
        Initialize a new Grouped object.

            *args:
              The names of the properties used to organize the contents in the order to use them.
              The outermost axis will group objects according to the first property, the second
              axis according to the second, etc.
            **kwargs:
              The property names and values that all contents in this object must share. Passing
              a property name as both a positional argument and a keyword will raise a ValueError.
        """
        ...
    @property
    def depth(self) -> int:
        """The number of axes this object has."""
        ...
    def __repr__(self) -> str: ...
    def add(self, data: Data[_T]) -> None:
        """
        Add the provided Data object to this group. Will raise a ValueError if the properties of
        \'data\' do not match the ones provided to the initializer.
        """
        ...