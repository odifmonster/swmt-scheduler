from app.schedule.demand.groups import ColorProps as ColorProps, \
    ColorGroupView as ColorGroupView, ColorGroup as ColorGroup, \
    GreigeProps as GreigeProps, GreigeGroupView as GreigeGroupView, \
    GreigeGroup as GreigeGroup, PriorityProps as PriorityProps, \
    PriorityGroupView as PriorityGroupView, PriorityGroup as PriorityGroup, \
    DemandGroupView as DemandGroupView, DemandGroup as DemandGroup

from typing import Unpack, Protocol
from abc import abstractmethod
import datetime
from app.support import PrettyArgsOpt, SuperView, Viewable
from app.support.groups import DataLike
from app.style import FabricStyle, GreigeStyle

class DemandLike(DataLike[int, PrettyArgsOpt], Protocol):
    """
    A protocol for Demand objects and their views.
    """
    @property
    def _prefix(self) -> str: ...
    @property
    @abstractmethod
    def id(self) -> int: ...
    @property
    @abstractmethod
    def item(self) -> FabricStyle: ...
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def color_num(self) -> str: ...
    @property
    @abstractmethod
    def yards(self) -> float: ...
    @property
    @abstractmethod
    def pounds(self) -> float: ...
    @property
    @abstractmethod
    def due_date(self) -> datetime.datetime: ...
    @abstractmethod
    def assign(self, pounds: float) -> None: ...
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]) -> str: ...
    
class DemandView(DemandLike, SuperView[DemandLike],
                 no_access=['assign'],
                 overrides=[],
                 dunders=['eq','hash']):
    ...

class Demand(DemandLike, Viewable[DemandView]):
    """
    A class for Demand objects. One Demand object represents a unique fabric
    item and priority combination.
    """
    def __init__(self, item: FabricStyle, yards: float, due_date: datetime.datetime) -> None:
        ...
    @property
    def id(self) -> int: ...
    @property
    def item(self) -> FabricStyle: ...
    @property
    def yards(self) -> float: ...
    @property
    def pounds(self) -> float: ...
    @property
    def due_date(self) -> datetime.datetime: ...
    def assign(self, pounds: float) -> None:
        """
        Assign some of this demand to a job/dye lot. Only accepts the number of pounds
        of greige assigned as an argument.
        """
        ...
    def unassign(self, pounds: float) -> None:
        """
        Unassign some of this demand to a job/dye lot. Only accepts the number of pounds
        of greige unassigned as an argument.
        """
        ...
    def view(self) -> DemandView: ...

EMPTY_DEMAND = Demand(...)