import datetime as dt
from app.support import HasID, SuperImmut
from app.style import FabricStyle
from app.materials import PortLoad
from app.schedule import DyeLot, DyeLotView
from app.schedule.demand.order import Order

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','orders','lots'),
          priv_attrs=('id','lots'), frozen=('*id','item','orders')):
    """
    A class for Req objects. Represents all the orders
    on a single item.
    """
    item: FabricStyle # the item of this requirement
    orders: tuple[Order, ...] # the orders that compose this requirement
    def __init__(self, item: FabricStyle, buckets: list[tuple[int, float]],
                 p1date: dt.datetime) -> None:
        """
        Initialize a new Req object.

            item:
              The item of this requirement.
            buckets:
              A list of pairs of priority numbers and their associated yards.
            p1date:
              The date and time the P1 truck is leaving.
        """
        ...
    @property
    def lots(self) -> list[DyeLotView]:
        """The DyeLots assigned to this requirement."""
        ...
    @property
    def total_yds_prod(self) -> float:
        """The total yards of this item that will be produced by the schedule."""
        ...
    def total_yds_by(self, date: dt.datetime) -> float:
        """The total yards of this item that will be produced by the given date."""
        ...
    def assign(self, ports: list[PortLoad]) -> DyeLot:
        """Assigns the given ports to this requirement. Returns the resulting dyelot."""
        ...
    def unassign(self, lview: DyeLotView) -> DyeLot:
        """Unassigns the given dyelot from this requirement. Returns the unassigned dyelot."""
        ...