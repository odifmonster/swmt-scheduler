from app.inventory.roll.roll import SizeClass as SizeClass, PARTIAL as PARTIAL, \
    SMALL as SMALL, NORMAL as NORMAL, LARGE as LARGE

from typing import Protocol, Unpack
from abc import abstractmethod
from app.support import PrettyArgsOpt, SuperView, Viewable
from app.support.groups import DataLike
from app.style import GreigeStyle

class RollLike(DataLike[str, PrettyArgsOpt], Protocol):
    """
    A protocol for (greige) Roll objects and their views.
    """
    @property
    def _prefix(self) -> str: ...
    @property
    @abstractmethod
    def id(self) -> str: ...
    @property
    @abstractmethod
    def item(self) -> GreigeStyle: ...
    @property
    @abstractmethod
    def weight(self) -> float: ...
    @property
    @abstractmethod
    def size_class(self) -> SizeClass: ...
    @abstractmethod
    def allocate(self, amount: float) -> None: ...
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]) -> str: ...

class RollView(RollLike, SuperView[RollLike], no_access=['allocate'],
               overrides=[], dunders=['eq','hash']):
    """
    A class for live, read-only views of Roll objects.
    """
    @property
    def id(self) -> str:
        """The unqiue id of this Roll in inventory."""
        ...
    @property
    def item(self) -> GreigeStyle: ...
    @property
    def weight(self) -> float: ...
    @property
    def size_class(self) -> SizeClass: ...
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]) -> str: ...

class Roll(RollLike, Viewable[RollView]):
    """
    A class for Roll objects. Groups together all relevant information about
    greige rolls, and has a basic method for allocating pounds of greige to
    dyelots.
    """
    def __init__(self, id: str, greige: GreigeStyle, weight: float) -> None: ...
    @property
    def id(self) -> str:
        """The unqiue id of this Roll in inventory."""
        ...
    @property
    def item(self) -> GreigeStyle: ...
    @property
    def weight(self) -> float: ...
    @property
    def size_class(self) -> SizeClass: ...
    def allocate(self, amount: float) -> None:
        """
        Decreases 'weight' by the given amount. Raises an error for invalid amounts.
        'size_class' will be recalculated accordingly.
        """
        ...
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]) -> str: ...
    def view(self) -> RollView: ...