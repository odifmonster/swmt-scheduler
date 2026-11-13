import datetime as dt
from app.support import HasID, SuperImmut
from app.style import FabricStyle
from app.materials import PortLoad
from app.schedule import DyeLot, DyeLotView
from app.schedule.demand.order import Order

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','orders','lots','avg_use','hard_orders',
                 'safety_order'),
          priv_attrs=('id','lots'), frozen=('*id','item','orders','avg_use')):
    """
    A class for Req objects. Represents all the orders
    on a single item.
    """
    item: FabricStyle # the item of this requirement
    orders: tuple[Order, ...] # the orders that compose this requirement
    avg_use: float # the average weekly yards of hard requirements
    def __init__(self, item: FabricStyle,
                 buckets: list[tuple[int, dt.datetime, float]],
                 safety: tuple[int, dt.datetime, float] | None = None) -> None:
        """
        Initialize a new Req object.

            item:
              The item of this requirement.
            buckets:
              A list of tuples of priority numbers, due dates, and
              their associated yards (the hard requirements).
            safety:
              An optional trailing bucket of safety stock to build
              once the hard requirements are covered. Same shape as
              a hard bucket. Ignored when its yards are not positive.
        """
        ...
    @property
    def lots(self) -> list[DyeLotView]:
        """The DyeLots assigned to this requirement."""
        ...
    @property
    def hard_orders(self) -> tuple[Order, ...]:
        """The orders of this requirement that are hard requirements."""
        ...
    @property
    def safety_order(self) -> Order | None:
        """The safety stock order of this requirement, if any."""
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
