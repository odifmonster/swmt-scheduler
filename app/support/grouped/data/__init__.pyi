from typing import Hashable
from app.support.protocols import HasID
from app.support.supers import SuperImmut, SuperView

class Data[T: Hashable](HasID[T], SuperImmut):
    """
    A class for Data objects. Any type that can be added to a Grouped object must subclass
    from this type. Provides an implementation of HasID and requires its instances to provide
    views of themselves.
    """
    def __init_subclass__(cls, mod_in_group: bool, attrs: tuple[str, ...] = tuple(),
                          priv_attrs: tuple[str, ...] = tuple(),
                          frozen: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new Data subclass.

            mod_in_group:
              A flag for indicating whether this type should be modifiable while inside a group.
              If False, you cannot set attribute values or call setter-like methods on this object
              while it is inside of a Grouped object.
            attrs:
              The non-mangled attributes of the class. '_prefix' and 'id' are added automatically.
            priv_attrs:
              The attributes whose names should be mangled to act as 'private' variables.
            frozen:
              The attributes to freeze. Private attributes can be marked with a preceding '*', and the
              following string will be mangled. A ValueError is raised if 'frozen' contains names not
              declared in 'attrs' or 'priv_attrs'. The private locations for '_prefix' and 'id' are
              added automatically, and inaccessible to subclasses.
        """
        ...
    def __init__(self, id: T, prefix: str, view: 'DataView[T]', priv: dict[str] = {}, **kwargs) -> None:
        """
        Initialize a new Data object.

            id:
              The unique id of this object.
            prefix:
              The prefix that identifies this object's type.
            view:
              A view linked to this object that shares all of its attributes.
            priv: (default {})
              A mapping from un-mangled private variable names to their values.
            **kwargs:
              Every keyword should be an attribute provided to the subclass initializer. The values are
              the corresponding values of those attributes.
        """
        ...
    def view(self) -> 'DataView[T]':
        """Returns a live, read-only view of this object."""
        ...

class DataView[T: Hashable](SuperView[HasID[T]]):
    """
    A class for views of Data objects.
    """
    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(), funcs: tuple[str, ...] = tuple(),
                          dunders: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new DataView subclass.

            attrs:
              The viewed attributes of the linked object. '_prefix' and 'id' are added automatically.
            funcs:
              The functions of the viewed object.
            dunders:
              The "dunder" or "magic" functions to use from the viewed type. 'eq' and 'hash' are added
              automatically
        """
        ...
    def __eq__(self, other: 'DataView[HasID[T]]') -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    @property
    def _prefix(self) -> str:
        """
        For internal use only. Prevents two objects of different types from being treated as
        equal.
        """
        ...
    @property
    def id(self) -> T:
        """The unique, hashable id of this object."""
        ...

def match_props(data: Data, props: dict[str]) -> bool:
    """
    Check whether some data matches the items of a properties dict.

        data:
          The data to check.
        props:
          The attributes and values to match against.
    
    Returns True iff for every attribute name in 'props', data.attribute = props[attribute]
    """
    ...

def repr_props(props: dict[str], indent: str = '  ') -> str:
    """Returns a string representation of a properties dict."""
    ...