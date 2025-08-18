from typing import TypeVar, Generic, Hashable, Any, Unpack
from app.support import ArgTup, SuperImmut, HasID, SuperView, Viewable

_T = TypeVar('_T', bound=Hashable)

class DataView(Generic[_T], SuperView[HasID[_T]]):
    """
    A base class for views of Data objects. Should not be instantiated directly.
    Defines correct view behavior for HasID protocol and related functions.
    """
    def __init_subclass__(cls, funcs: list[str] = [], dunders: list[str] = [],
                          attrs: list[str] = [], vfuncs: list[str] = [],
                          vdunds: list[str] = [], vattrs: list[str] = []) -> None: ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> _T: ...

class Data(Generic[_T], HasID[_T], Viewable[DataView[_T]], SuperImmut):
    """
    A base class for Data objects. Any type that wants to be used as the contents of
    a Grouped object must subclass from Data. Should not be instantiated directly.
    Defines correct behavior for HasID protocol and related functions. Requires
    implementation of 'view' method.
    """
    def __init_subclass__(cls, fg_flag: bool = True, dattrs: ArgTup = tuple(),
                          dpriv_attrs: ArgTup = tuple(), dfrozen: ArgTup = tuple()) -> None:
        """
        Create a new Data type. If no additional attributes are defined in 'dfrozen',
        only the private references for 'id' and '_prefix' will be used. If 'fg_flag' is
        set to False, then instances can be modified while in Grouped objects.
        """
        ...
    def __init__(self, id: _T, prefix: str, view: DataView[_T], priv: dict[str, Any] = {},
                 **kwargs: Unpack[dict[str, Any]]) -> None:
        """
        Initialize a new Data object.

            id:
              The unique id of this object
            prefix:
              The common prefix used for all objects of this type.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> _T: ...
    def view(self) -> DataView[_T]: ...