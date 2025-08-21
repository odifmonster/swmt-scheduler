from app.schedule.req.groups import ReqColorKeys as ReqColorKeys, \
    ReqGreigeKeys as ReqGreigeKeys, DemandKeys as DemandKeys, ReqColorView as ReqColorView, \
    ReqGreigeView as ReqGreigeView, DemandView as DemandView, ReqColorGroup as ReqColorGroup, \
    ReqGreigeGroup as ReqGreigeGroup, Demand as Demand

from typing import Literal
import datetime as dt
from app.support import SuperView
from app.groups import DataView, Data
from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll
from app.schedule import DyeLot, DyeLotView

class Bucket(SuperView['Req']):
    """
    A class for "buckets" of a requirement. One bucket contains information regarding the total yards
    of a given item and the date they must be finished. It tracks the number of late yards and how
    late they will be using the DyeLots currently assigned to the overall requirement.
    """
    item: FabricStyle
    def __init__(self, link: 'Req', yds: float, date: dt.datetime) -> None:
        """
        Initialize a new Bucket object, which is linked to a Req object for some fabric item.

            link:
              The Req object this bucket is part of.
            yds:
              The cumulative total yards in this bucket (that is, the total yards of the item
              that must be completed by the given date).
            date:
              The date and time the truck for this bucket will leave.
        """
        ...
    def __repr__(self) -> str: ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style for this object."""
        ...
    @property
    def color(self) -> Color:
        """The color for this object."""
        ...
    @property
    def lots(self) -> list[DyeLotView]:
        """The DyeLots used to fulfill the total requirement that contains this bucket."""
        ...
    @property
    def date(self) -> dt.datetime:
        """The date and time the truck for this bucket will leave."""
        ...
    @property
    def yds(self) -> float:
        """The remaining yards needed to fulfill this bucket on time."""
        ...
    @property
    def lbs(self) -> float:
        """The remaining pounds needed to fulfill this bucket on time."""
        ...
    @property
    def total_yds(self) -> float:
        """The total yards remaining to fulfill this bucket, ignoring the due date."""
        ...
    @property
    def total_lbs(self) -> float:
        """The total pounds remaining to fulfill this bucket, ignoring the due date."""
        ...
    @property
    def late_yds(self) -> list[tuple[float, dt.timedelta]]:
        """
        A tuple containing the number of yards in this bucket that will miss their truck, and
        the amount of time they will miss it by.
        """
        ...
    
class ReqView(DataView[str]):
    """
    A class for views of Req objects.
    """
    item: FabricStyle
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def color(self) -> Color: ...
    @property
    def lots(self) -> list[DyeLotView]: ...
    def __repr__(self) -> str: ...
    def bucket(self, pnum: Literal[1, 2, 3, 4]) -> Bucket: ...
    def late_yd_buckets(self) -> list[tuple[float, dt.timedelta]]: ...
    def assign_lot(self, rolls: list[AllocRoll], pnum: int) -> DyeLot: ...
    def unassign_lot(self, lot: DyeLotView) -> None: ...

class Req(Data[str]):
    """
    A class for fabric item requirements. The requirements are broken down into 4 "buckets", where
    each bucket has a due date attached. The total requirements are only represented in the number
    of late yards, otherwise buckets should be used.
    """
    item: FabricStyle
    def __init__(self, item: FabricStyle, p1date: dt.datetime,
                 buckets: tuple[float, float, float, float]) -> None:
        """
        Initialize a new Req object.

            item:
              The fabric item for this requirement.
            p1date:
              The date of the P1 truck. The rest of the dates are calculated relative to this one.
            buckets:
              The yards in each priority bucket.
        """
        ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style of this requirement's item."""
        ...
    @property
    def color(self) -> Color:
        """The color of this requirement's item."""
        ...
    @property
    def lots(self) -> list[DyeLotView]:
        """The views of the lots assigned to this requirement."""
        ...
    def bucket(self, pnum: Literal[1, 2, 3, 4]) -> Bucket:
        """
        Get a Bucket by priority number.

            pnum:
              The priority number (1-4) of the desired bucket.

        Returns the Bucket object corresponding to the given priority.
        """
        ...
    def late_yd_buckets(self) -> list[tuple[float, dt.timedelta]]:
        """
        Returns a list of any requirements (in yards) that will not be fulfilled on time and
        the amount of time they will miss their respective trucks by. If a requirement will not
        be fulfilled at all, the time defaults to one week.
        """
        ...
    def assign_lot(self, rolls: list[AllocRoll], pnum: int) -> DyeLot:
        """
        Create and assign a DyeLot with the given allocated rolls to a bucket of this requirement.

            rolls:
              The list of allocated rolls to use.
            pnum:
              The priority number of the targeted bucket.
        
        Returns the newly created DyeLot object.
        """
        ...
    def unassign_lot(self, lot: DyeLotView) -> None:
        """
        Unassign the provided DyeLot from this requirement. It will no longer be factored into
        the remaining and late quantity calculations for each bucket.

            lot:
              The view of the DyeLot to unassign.
        """
        ...
    def view(self) -> ReqView: ...