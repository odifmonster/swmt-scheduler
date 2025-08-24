from typing import Callable, Concatenate

def setter_like[U, **P, T](func: Callable[Concatenate[U, P], T]) -> Callable[Concatenate[U, P], T]:
    """
    A decorator for indicating a function is "setter-like". If a View object tries to call a
    setter-like method, it will raise a RuntimeError.
    """
    ...

class SuperView[T]:
    """
    A super class for creating types that can "view" information about other objects. "Viewed"
    attributes are live and read-only.
    """
    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(), funcs: tuple[str, ...] = tuple(),
                          dunders: tuple[str, ...] = tuple()) -> None:
        """
        Initialize a new subclass of SuperView.

            attrs:
              The viewed attributes of the linked object.
            funcs:
              The functions of the viewed object.
            dunders:
              The "dunder" or "magic" functions to use from the viewed type.
        """
        ...
    def __init__(self, link: T) -> None:
        """
        Initialize a new SuperView object.

            link:
              The viewed object.
        """
        ...