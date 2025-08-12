from typing import ParamSpec, TypeVar, Generic, Callable, Any

_P = ParamSpec('_P')
_T = TypeVar('_T')

def setter_like(f: Callable[_P, _T]) -> Callable[_P, _T]:
    """
    A function decorator for marking methods that mutate instances of a class. Methods
    decorated with 'setter_like' cannot be called by view objects.
    """
    ...

class SuperView(Generic[_T]):
    """
    A class for views of other objects. Subclassing from SuperView creates a type whose
    methods and attributes are partly derived from a linked object.
    """
    def __init_subclass__(cls, funcs: list[str] = [], dunders: list[str] = [],
                          attrs: list[str] = [],
                          vfuncs: list[str] = [], vdunds: list[str] = [],
                          vattrs: list[str] = []) -> None:
        """
        Create a new view type. 'vfuncs', 'vdunds', and 'vattrs' allow you to define methods
        and attributes specific to the view type (if it should differ structurally from what
        it views).

            funcs:
              All the non-dunder functions from the viewed object the view type has access to.
            dunders:
              All the dunder functions (no underscores) from the viewed object the view type has
              access to.
            attrs:
              Same as 'funcs' and 'dunders' but for value attributes and properties.
        """
        ...
    def __init__(self, link: _T) -> None:
        """
        Initialize a new view object.

            link:
              The object to be viewed.
        """
        ...