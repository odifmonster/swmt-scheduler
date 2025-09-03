from typing import Protocol
import datetime as dt
from app.support.grouped import Data, DataView
from app.style import FabricStyle, GreigeStyle, Color
from app.materials import PortLoad
from app.schedule import DyeLot, DyeLotView

class _Req(Protocol):
    item: FabricStyle
    @property
    def lots(self) -> list[DyeLotView]: ...
    @property
    def total_yds_prod(self) -> float: ...
    def total_yds_by(date: dt.datetime) -> float: ...
    def assign(rolls: list[PortLoad]) -> DyeLot: ...
    def unassign(lview: DyeLotView) -> DyeLot: ...

class Order(Data[str], mod_in_group=True,
            attrs=('item','greige','color','yds','init_yds','cum_yds','total_yds',
                   'lbs','init_lbs','cum_lbs','total_lbs','pnum','due_date'),
            priv_attrs=('req','init_cur_yds','init_cum_yds'),
            frozen=('*req','*init_cur_yds','*init_cum_yds','item','pnum','due_date')):
    """
    A class for Order objects. This represents a required quantity
    of an item and a due date. Orders will track their fulfillment
    status against their requirement, the total requirement on that
    item, and their due dates.
    """
    item: FabricStyle # the item for this order
    pnum: int # the priority number of this order
    due_date: dt.datetime # the due date of this order
    def __init__(self, req: _Req, item: FabricStyle, pnum: int, cur_yds: float,
                 cum_yds: float) -> None:
        """
        Initialize a new Order object.

            req:
              The overall requirement this order is part of.
            item:
              The item this order is for.
            pnum:
              The priority number of this order.
            cur_yds:
              The number of yards in this order.
            cum_yds:
              The total yards to produce by this order's due date.
            p1date:
              The date and time the P1 truck is leaving.
        """
        ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style of this order's item."""
        ...
    @property
    def color(self) -> Color:
        """The color of this order's item."""
        ...
    @property
    def yds(self) -> float:
        """The remaining yards needed to fulfill only this order by its due date."""
        ...
    @property
    def init_yds(self) -> float:
        """The initial yards in this order."""
        ...
    @property
    def cum_yds(self) -> float:
        """The cumulative remaining yards needed to fulfill the requirement by this due date."""
        ...
    @property
    def total_yds(self) -> float:
        """The total remaining yards needed to fulfill this requirement, ignoring due date."""
        ...
    @property
    def lbs(self) -> float:
        """The remaining pounds needed to fulfill only this order by its due date."""
        ...
    @property
    def init_lbs(self) -> float:
        """The initial pounds in this order."""
        ...
    @property
    def cum_lbs(self) -> float:
        """The cumulative remaining pounds needed to fulfill the requirement by this due date."""
        ...
    @property
    def total_lbs(self) -> float:
        """The total remaining pounds needed to fulfill this requirement, ignoring due date."""
        ...
    def late_table(self, next_avail: dt.datetime) -> list[tuple[float, dt.timedelta]]:
        """
        Returns a list of pairs containing yards and how late
        they will be compared to this order's due date.
        """
        ...
    def assign(self, ports: list[PortLoad]) -> DyeLot:
        """Assign the given ports to this order. Returns the resulting dyelot."""
        ...
    def unassign(self, lview: DyeLotView) -> DyeLot:
        """Unassign the given dyelot from this order. Returns the unassigned dyelot."""
        ...

class OrderView(DataView[str],
                attrs=('item','greige','color','yds','init_yds','cum_yds','total_yds',
                       'lbs','init_lbs','cum_lbs','total_lbs','pnum','due_date'),
                funcs=('late_table','assign','unassign'),
                dunders=('repr',)):
    """
    A class for views of Order objects.
    """
    pnum: int # the priority number of this order
    due_date: dt.datetime # the due date of this order
    def __init__(self, link: Order) -> None: ...
    @property
    def item(self) -> FabricStyle: ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style of this order's item."""
        ...
    @property
    def color(self) -> Color:
        """The color of this order's item."""
        ...
    @property
    def yds(self) -> float:
        """The remaining yards needed to fulfill only this order by its due date."""
        ...
    @property
    def init_yds(self) -> float:
        """The initial yards in this order."""
        ...
    @property
    def cum_yds(self) -> float:
        """The cumulative remaining yards needed to fulfill the requirement by this due date."""
        ...
    @property
    def total_yds(self) -> float:
        """The total remaining yards needed to fulfill this requirement, ignoring due date."""
        ...
    @property
    def lbs(self) -> float:
        """The remaining pounds needed to fulfill only this order by its due date."""
        ...
    @property
    def init_lbs(self) -> float:
        """The initial pounds in this order."""
        ...
    @property
    def cum_lbs(self) -> float:
        """The cumulative remaining pounds needed to fulfill the requirement by this due date."""
        ...
    @property
    def total_lbs(self) -> float:
        """The total remaining pounds needed to fulfill this requirement, ignoring due date."""
        ...
    def late_table(self, next_avail: dt.datetime) -> list[tuple[float, dt.timedelta]]:
        """
        Returns a list of pairs containing yards and how late
        they will be compared to this order's due date.
        """
        ...
    def assign(self, ports: list[PortLoad]) -> DyeLot:
        """Assign the given ports to this order. Returns the resulting dyelot."""
        ...
    def unassign(self, lview: DyeLotView) -> DyeLot:
        """Unassign the given dyelot from this order. Returns the unassigned dyelot."""
        ...