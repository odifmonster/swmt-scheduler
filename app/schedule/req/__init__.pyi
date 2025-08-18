from app.schedule.req.groups import DemandView as DemandView, Demand as Demand, \
    ReqGreigeView as ReqGreigeView, ReqGreigeGroup as ReqGreigeGroup, \
    ReqColorView as ReqColorView, ReqColorGroup as ReqColorGroup, \
    ReqItemView as ReqItemView, ReqItemGroup as ReqItemGroup, \
    ReqPriorView as ReqPriorView, ReqPriorGroup as ReqPriorGroup

import datetime as dt
from app.groups import DataView, Data
from app.style import GreigeStyle, FabricStyle, Color, color

class ReqView(DataView[str]):
    """
    A class for views of Req objects.
    """
    item: FabricStyle
    due_date: dt.datetime
    def __init__(self, link: 'Req') -> None: ...
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def color(self) -> Color: ...
    @property
    def shade(self) -> color.ShadeGrade: ...
    @property
    def yds(self) -> float: ...
    @property
    def lbs(self) -> float: ...
    def __repr__(self) -> str: ...
    def fulfill(self, lbs: float) -> None: ...

class Req(Data[str]):
    """
    A class for fabric requirements. A requirement is uniquely identified by its item and due date.
    """
    item: FabricStyle
    due_date: dt.datetime
    def __init__(self, item: FabricStyle, yds: float, due_date: dt.datetime,
                 subscriber: 'Req | None' = None) -> None:
        """
        Initialize a new Req object.

            item:
              The fabric item to produce.
            yds:
              The quantity in this requirement bucket.
            due_date:
              The due_date for this requirement.
            subscriber: (default None)
              An optional requirement that will track the overflow from this object. That is, if this
              requirement is fulfilled with more yards than it needs, the excess yards will be used to
              fulfill the subscriber.
        """
        ...
    @property
    def greige(self) -> GreigeStyle:
        """The GreigeStyle of the item for this requirement."""
        ...
    @property
    def color(self) -> Color:
        """The Color of the item for this requirement."""
        ...
    @property
    def shade(self) -> color.ShadeGrade:
        """The ShadeGrade associated with this object's color."""
        ...
    @property
    def yds(self) -> float:
        """The remaining unfulfilled yards on this requirement."""
        ...
    @property
    def lbs(self) -> float:
        """The remaining unfulfilled pounds on this requirement."""
        ...
    def __repr__(self) -> str: ...
    def fulfill(self, lbs: float) -> None:
        """
        Decreases the remaining required yards using the provided lbs.
        """
        ...