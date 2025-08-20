from typing import Protocol, Literal
import datetime as dt
from app.support import HasID, SuperImmut, SuperView, Viewable
from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll

class _Bucket(Protocol):
    """
    A class for "buckets" of a requirement. One bucket contains information regarding the total yards
    of a given item and the date they must be finished. It tracks the number of late yards and how
    late they will be using the DyeLots currently assigned to the overall requirement.
    """
    item: FabricStyle
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
    def late_yds(self) -> tuple[float, dt.timedelta]:
        """
        A tuple containing the number of yards in this bucket that will miss their truck, and
        the amount of time they will miss it by.
        """
        ...
    @property
    def late_lbs(self) -> tuple[float, dt.timedelta]:
        """
        A tuple containing the number of pounds in this bucket that will miss their truck, and
        the amount of time they will miss it by.
        """
        ...

class _ReqView(Protocol):
    """
    A class for fabric item requirements. The requirements are broken down into 4 "buckets", where
    each bucket has a due date attached. The total requirements are only represented in the number
    of late yards, otherwise buckets should be used.
    """
    item: FabricStyle
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
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
    def bucket(self, pnum: Literal[1, 2, 3, 4]) -> _Bucket:
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
    def late_lb_buckets(self) -> list[tuple[float, dt.timedelta]]:
        """
        Returns a list of any requirements (in pounds) that will not be fulfilled on time and
        the amount of time they will miss their respective trucks by. If a requirement will not
        be fulfilled at all, the time defaults to one week.
        """
        ...
    def assign_lot(self, rolls: list[AllocRoll]) -> DyeLot:
        """
        Create and assign a DyeLot with the given allocated rolls to this requirement.

            rolls:
              The list of allocated rolls to use.
        
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

class DyeLotView(SuperView['DyeLot']):
    """
    A class for views of DyeLot objects.
    """
    start: dt.datetime
    end: dt.datetime
    rolls: tuple[AllocRoll, ...]
    item: FabricStyle
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> int: ...
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def color(self) -> Color: ...
    @property
    def lbs(self) -> float: ...
    @property
    def yds(self) -> float: ...
    @property
    def req(self) -> _ReqView: ...
    @property
    def due_date(self) -> dt.datetime: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: 'DyeLotView') -> bool: ...
    def __hash__(self) -> int: ...

class DyeLot(HasID[int], Viewable[DyeLotView], SuperImmut):
    """
    A class for DyeLot objects. Must be initialized with the rolls that will be allocated to it
    and a link to the requirement it is fulfilling. Its start and end attributes are mutable, but
    should generally only be modified by the enclosing Jobs unless being used in unittests.
    """
    start: dt.datetime
    end: dt.datetime
    rolls: tuple[AllocRoll, ...]
    item: FabricStyle
    def __init__(self, rolls: list[AllocRoll], item: FabricStyle, rview: _ReqView,
                 pnum: int) -> None:
        """
        Initialize a new DyeLot object.

            rolls:
              The allocated rolls to use for this lot.
            item:
              The item that will be produced by this lot.
            rview:
              A ReqView that links to the requirement this lot aims to fulfill.
            pnum:
              The priority number of the bucket this lot is targeting.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> int: ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style used for this lot."""
        ...
    @property
    def color(self) -> Color:
        """The color used for this lot."""
        ...
    @property
    def lbs(self) -> float:
        """The total pounds in this lot."""
        ...
    @property
    def yds(self) -> float:
        """The total yards produced by this lot."""
        ...
    @property
    def req(self) -> _ReqView:
        """A view of the Req object this lot is fulfilling."""
        ...
    @property
    def due_date(self) -> dt.datetime:
        """The date of the truck the yards from this lot should be on."""
        ...