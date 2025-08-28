from typing import Hashable, Unpack, Generator
from app.support import SuperImmut
from app.support.grouped import Data, DataView

class Atom[T: Hashable](SuperImmut, attrs=('depth','n_items'), priv_attrs=('props','data'),
                        frozen=('*props',)):
    """
    A class for Atom objects. Acts as a container for one individual
    Data object, but allows it to be treated like a Grouped object.
    """
    def __init__(self, data: Data[T], *args: Unpack[tuple[str, ...]]) -> None:
        """
        Initialize a new Atom object.

            data:
              The data this atom will hold.
            *args:
              The names of the attributes whose values determine how
              this data is grouped. If the same data is removed and
              then added after changing one of these attributes, it
              will be stored in a different atom. Raises a ValueError
              if 'id' is not included.
        """
        ...
    def __len__(self) -> int:
        """The number of subgroups this object contains."""
        ...
    def __iter__(self) -> Generator[tuple[()]]:
        """Will only generate a single empty tuple if this atom is non-empty."""
        ...
    def __contains__(self, key: tuple[()]) -> bool:
        """Returns True iff 'key' points to a non-empty sub-group."""
        ...
    def __getitem__(self, key: tuple[()]) -> DataView[T]:
        """
        Returns a view of the subgroup with the properties listed in
        the key. The key's elements must be in the same order as the
        group's axes. Passing an empty tuple is equivalent to calling
        the 'view' method.
        """
        ...
    @property
    def depth(self) -> int:
        """
        The number of "axes" in this object (i.e., the number of
        attributes being used to group the contents of this object).
        """
        ...
    @property
    def n_items(self) -> int:
        """The total number of items in this object."""
        ...
    def iterkeys(self) -> Generator[tuple[()]]:
        """
        Returns a generator of the "full" keys of this object. Every
        tuple generated will return an individual item when passed to
        __getitem__.
        """
        ...
    def itervalues(self) -> Generator[DataView[T]]:
        """Returns a generator of the individual items contained in this Grouped object."""
        ...
    def get(self, id: T) -> DataView[T]:
        """Get the view of a Data object by its id."""
        ...
    def add(self, data: Data[T]) -> None:
        """Add the provided data to this object."""
        ...
    def remove(self, dview: DataView[T], remkey: bool = False) -> Data[T]:
        """Remove data from this object using its view."""
        ...