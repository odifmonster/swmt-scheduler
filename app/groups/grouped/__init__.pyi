from typing import TypeVar, Generic, Unpack, Hashable, Generator
from app.groups import Data, DataView

_T = TypeVar('_T', bound=Hashable)
_U = TypeVar('U', bound=Hashable)

class _Atom(Generic[_T]): # INTERNAL USE ONLY
    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Generator[tuple[()]]: ...
    def __contains__(self, key: _T) -> bool: ...
    def add(self, data: Data[_T]) -> None: ...
    def remove(self, dview: DataView[_T]) -> Data[_T]: ...

class Grouped(Generic[_T, _U]):
    """
    A base class for Grouped objects. Must be subclassed to instantiate. The type parameters
    are 1) the type of the 'id' attribute of the Data objects this will hold, and 2) the
    type of property that defines the outermost "axis". This class provides mapping-like
    functions for grouping objects by several properties.
    """
    def __init__(self, *args: Unpack[tuple[str, ...]], **kwargs) -> None:
        """
        Initialize a new Grouped object.

            *args:
              The names of the properties used to organize the Grouped object.
            **kwargs:
              A series of attribute=value pairs that will restrict the kinds of data that can
              be added. Any overlap between the strings from the positional arguments and the
              keywords will result in a ValueError.
        """
        ...
    @property
    def depth(self) -> int:
        """The number of axes for this Grouped object."""
        ...
    def __repr__(self) -> str: ...
    def __len__(self) -> int:
        """The number of non-empty sub-groups in this object."""
        ...
    def __iter__(self) -> Generator[_U]:
        """Iterates over the keys that correspond to non-empty sub-groups."""
        ...
    def __contains__(self, key: _U) -> bool:
        """Returns True iff the key corresponds to a non-empty sub-group."""
        ...
    def make_atom(self, data: Data[_T], *args: Unpack[tuple[str, ...]]) -> _Atom[_T]:
        """
        A helper function for creating new "atoms". To be used in the implementation of
        'make_group'.
        """
        ...
    def make_group(self, data: Data[_T], prev_props: dict[str]) -> 'Grouped[_T] | _Atom[_T]':
        """
        This function must be implemented in all subclasses. The default behavior raises a
        NotImplementedError().
        """
        ...
    def add(self, data: Data[_T]) -> None:
        """Add data to this object."""
        ...
    def remove(self, dview: DataView[_T]) -> Data[_T]:
        """
        Remove data from this object using its view.

          dview:
            The view of the data to remove. Does not technically have to be on the original
            object, but it will fail if 'dview' does not share all the required attributes
            with the targeted Data object.

          returns:
            The Data object corresponding to the provided view.
        """
        ...