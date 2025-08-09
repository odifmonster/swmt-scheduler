from typing import TypeVar, TypeVarTuple, Protocol, Generic, Any, \
    Iterator, Hashable, \
    Unpack
from abc import abstractmethod
from app.support import HasID, SupportsPretty, PrettyArgsOpt, Viewable, \
    SuperView

_T_D = TypeVar('_T_D', str, int)
_T_D_co = TypeVar('_T_D_co', bound=PrettyArgsOpt, covariant=True)

class DataLike(Protocol[_T_D, _T_D_co], HasID[_T_D], SupportsPretty[_T_D_co]):
    """
    A protocol for objects that can be added to groups. Combines HasID and
    SupportsPretty protocols.
    """
    ...

_T_V_co = TypeVar('_T_V_co', bound=PrettyArgsOpt, covariant=True)
_T_Vs = TypeVarTuple('_T_Vs')

class ValueLike(Protocol[_T_D, _T_V_co, _T_D_co, *_T_Vs], SupportsPretty[_T_V_co]):
    """
    A protocol for objects that are values of groups.
    """
    @abstractmethod
    def __len__(self) -> int: ...
    @abstractmethod
    def __iter__(self) -> Iterator: ...
    @abstractmethod
    def __getitem__(self, key: tuple) -> 'ValueLike[_T_D, Any, _T_D_co] | DataLike[_T_D, _T_D_co]':
        ...
    @abstractmethod
    def add(self, data: DataLike[_T_D, _T_D_co]) -> None: ...
    @abstractmethod
    def remove(self, id: _T_D) -> DataLike[_T_D, _T_D_co]: ...

_Empty = tuple[()]

class AtomLike(Protocol[_T_D, _T_D_co], ValueLike[_T_D, _T_D_co, _T_D_co]):
    """
    A protocol for "atoms" of a group. These represent individual elements of a group,
    but support group-like functions for the purpose of properly abstracting group
    operations.
    """
    @property
    @abstractmethod
    def data(self) -> DataLike[_T_D, _T_D_co]: ...
    @property
    @abstractmethod
    def is_empty(self) -> bool: ...
    def __iter__(self) -> Iterator[_Empty]: ...
    def __getitem__(self, key: _Empty) -> DataLike[_T_D, _T_D_co]: ...
    @abstractmethod
    def add(self, data: Viewable[DataLike[_T_D, _T_D_co]]) -> None: ...
    @abstractmethod
    def remove(self, id: _T_D) -> Viewable[DataLike[_T_D, _T_D_co]]: ...
    def pretty(self, **kwargs: Unpack[_T_D_co]) -> str: ...

class AtomView(Generic[_T_D, _T_D_co], AtomLike[_T_D, _T_D_co],
               SuperView[AtomLike[_T_D, _T_D_co]],
               no_access=['add', 'remove'], overrides=[]):
    """
    A live, read-only view of an Atom object. Cannot use 'add' or 'remove' methods.
    """
    ...

class Atom(Generic[_T_D, _T_D_co], AtomLike[_T_D, _T_D_co],
           Viewable[AtomView[_T_D, _T_D_co]]):
    """
    The concrete and mutable implementation of the AtomLike protocol.
    """
    ...
    def __init__(self) -> None: ...

_U_G = TypeVar('_U_G', bound=Hashable)
_U_Gs = TypeVarTuple('_U_Gs')

class GroupedLike(Protocol[_T_D, _T_D_co, _U_G, *_U_Gs],
                  ValueLike[_T_D, PrettyArgsOpt, _T_D_co, _U_G, *_U_Gs]):
    """
    A protocol for Grouped objects and their views.
    """
    @abstractmethod
    def __len__(self) -> int:
        """The length of the outermost axis."""
        ...
    @abstractmethod
    def __iter__(self) -> Iterator[_U_G]:
        """Iterator over the keys in the outermost axis."""
        ...
    @abstractmethod
    def __contains__(self, key: _U_G) -> bool: ...
    @abstractmethod
    def __getitem__(self, key: _U_G | tuple) -> 'DataLike[_T_D, _T_D_co] | GroupedLike[_T_D, _T_D_co, Unpack[tuple[Any, ...]]]':
        """
        Grouped objects support multi-indexing. The 'key' can be a single value
        or a tuple of any length up to the number of axes. The returned value
        will always be a view.
        """
        ...
    @abstractmethod
    def add(self, data: Viewable[DataLike[_T_D, _T_D_co]]) -> None: ...
    @abstractmethod
    def remove(self, id: _T_D) -> Viewable[DataLike[_T_D, _T_D_co]]: ...
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]) -> str: ...

class GroupedView(Generic[_T_D, _T_D_co, _U_G, *_U_Gs],
                  GroupedLike[_T_D, _T_D_co, _U_G, *_U_Gs],
                  SuperView[GroupedLike[_T_D, _T_D_co, _U_G, *_U_Gs]],
                  no_access=['add','remove'],
                  overrides=[],
                  dunders=['len','iter','contains','getitem']):
    """A live, read-only view of a Grouped object."""
    ...

class Grouped(Generic[_T_D, _T_D_co, _U_G, *_U_Gs],
              GroupedLike[_T_D, _T_D_co, _U_G, *_U_Gs],
              Viewable[GroupedView[_T_D, _T_D_co, _U_G, *_U_Gs]]):
    """
    The Grouped type. This is a mapping-like class with some additional useful
    functionality. A Grouped object can have a set of properties which all its
    contents must share, and can have multiple 'axes' (which represent an individual
    property and a set of corresponding values).
    """
    def __init__(self,
                 *unbound: Unpack[tuple[str, ...]],
                 **props: Unpack[dict[str, Any]]) -> None:
        """
        Create a new Grouped object. Can pass an arbitrary number of strings which
        will be used to organize the contents by property. The keyword arguments
        must be in the form attr=val, where 'attr' is an attribute of the data the object
        will hold (not passed as a positional argument), and 'val' is the value every
        data object must have.
        """
        ...
    def __len__(self) -> int:
        """The length of the outermost axis."""
        ...
    def __iter__(self) -> Iterator[_U_G]:
        """Iterator over the keys in the outermost axis."""
        ...
    def __contains__(self, key: _U_G) -> bool: ...
    def __getitem__(self, key: _U_G | tuple) -> 'DataLike[_T_D, _T_D_co] | GroupedLike[_T_D, _T_D_co, Unpack[tuple[Any, ...]]]':
        """
        Grouped objects support multi-indexing. The 'key' can be a single value
        or a tuple of any length up to the number of axes. The returned value
        will always be a view.
        """
        ...
    def add(self, data: Viewable[DataLike[_T_D, _T_D_co]]) -> None:
        """
        Adds the provided data to this object. A ValueError is thrown when it does
        not have the required property values. The data is automatically organized
        according to the unbound property values.
        """
        ...
    def remove(self, id: _T_D) -> Viewable[DataLike[_T_D, _T_D_co]]:
        """
        Remove data from this object by id. Returns the removed data.
        """
        ...
    def view(self) -> GroupedView[_T_D, _T_D_co, _U_G, *_U_Gs]: ...