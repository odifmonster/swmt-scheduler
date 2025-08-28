from app.support.grouped.data import Data as Data, DataView as DataView, match_props as match_props, \
    repr_props as repr_props
from app.support.grouped.atom import Atom as Atom

from typing import Hashable, Unpack, Generator
from app.support import SuperImmut, SuperView

class Grouped[T: Hashable, U: Hashable](SuperImmut):
    """
    A class for Grouped objects. This class is mapping-like, but
    organizes its contents automatically along multiple "axes", which
    are defined by the values of certain attributes of the contents.
    """
    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(),
                          priv_attrs: tuple[str, ...] = tuple(),
                          frozen: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new Grouped subtype. Takes no arguments, defines
        behavior relating to private and immutable attributes.
        """
        ...
    def __init__(self, view: 'GroupedView[T, U]', *args: Unpack[tuple[str, ...]], **kwargs) -> None:
        """
        Initialize a new Grouped object.

            *args:
              The "unbound" attributes of the data this object will hold.
              These are the attributes that will be used to organize the group's
              contents.
            **kwargs:
              The "bound" attributes of the data this object will hold. All data
              added must have attributes with values as defined by the keyword
              arguments and values.
        """
        ...
    def __len__(self) -> int:
        """The number of subgroups this object contains."""
        ...
    def __iter__(self) -> Generator[U]:
        """Iterates over the keys that correspond to non-empty subgroups."""
        ...
    def __contains__(self, key: U) -> bool:
        """Returns True iff 'key' points to a non-empty sub-group."""
        ...
    def __getitem__(self, key: U | tuple) -> 'GroupedView[T] | DataView[T]':
        """
        Returns a view of the subgroup with the properties listed in the key. The
        key's elements must be in the same order as the group's axes. Passing an
        empty tuple is equivalent to calling the 'view' method.
        """
        ...
    @property
    def depth(self) -> int:
        """
        The number of "axes" in this object (i.e., the number of attributes being
        used to group the contents of this object).
        """
        ...
    @property
    def n_items(self) -> int:
        """The total number of items in this object."""
        ...
    def make_group(self, data: Data[T], **kwargs) -> 'Grouped[T] | Atom[T]':
        """
        This function must be overridden in subclasses. It should return the new
        subgroup that corresponds to the provided data.
        """
        ...
    def iterkeys(self) -> Generator[tuple[U, *tuple]]:
        """
        Returns a generator of the "full" keys of this object. Every tuple
        generated will return an individual item when passed to __getitem__.
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
    def view(self) -> 'GroupedView[T, U]':
        """Returns a live, read-only view of this object."""
        ...

class GroupedView[T: Hashable, U: Hashable](SuperView[Grouped[T, U]]):
    """
    A class for views of Grouped objects.
    """
    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(), funcs: tuple[str, ...] = tuple(),
                          dunders: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new subclass of GroupedView.

            attrs:
              The viewed attributes of the linked Grouped object. 'n_items'
              and 'depth' are added automatically.
            funcs:
              The functions of the viewed object. 'make_group', 'iterkeys',
              'itervalues', 'get', 'add', and 'remove' are added
              automatically.
            dunders:
              The "dunder" or "magic" functions to use from the viewed type.
              'len', 'iter', 'contains', 'getitem', and 'repr' are added
              automatically.
        """
        ...
    def __len__(self) -> int:
        """The number of subgroups this object contains."""
        ...
    def __iter__(self) -> Generator[U]:
        """Iterates over the keys that correspond to non-empty subgroups."""
        ...
    def __contains__(self, key: U) -> bool:
        """Returns True iff 'key' points to a non-empty sub-group."""
        ...
    def __getitem__(self, key: U | tuple) -> 'GroupedView[T] | DataView[T]':
        """
        Returns a view of the subgroup with the properties listed in the key. The
        key's elements must be in the same order as the group's axes. Passing an
        empty tuple is equivalent to calling the 'view' method.
        """
        ...
    @property
    def depth(self) -> int:
        """
        The number of "axes" in this object (i.e., the number of attributes being
        used to group the contents of this object).
        """
        ...
    @property
    def n_items(self) -> int:
        """The total number of items in this object."""
        ...
    def make_group(self, data: Data[T], **kwargs) -> 'Grouped[T] | Atom[T]':
        """
        This function must be overridden in subclasses. It should return the new
        subgroup that corresponds to the provided data.
        """
        ...
    def iterkeys(self) -> Generator[tuple[U, *tuple]]:
        """
        Returns a generator of the "full" keys of this object. Every tuple
        generated will return an individual item when passed to __getitem__.
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
    def remove(self, dview: DataView[T]) -> Data[T]:
        """Remove data from this object using its view."""
        ...