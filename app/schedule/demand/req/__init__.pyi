import datetime as dt
from app.support import HasID, SuperImmut
from app.style import FabricStyle
from app.materials import PortLoad
from app.schedule import DyeLot, DyeLotView
from app.schedule.demand.order import Order

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','orders','lots'),
          priv_attrs=('id','lots'), frozen=('*id','item','orders')):
    item: FabricStyle
    orders: tuple[Order, ...]
    def __init__(self, item: FabricStyle, buckets: list[tuple[int, float]],
                 p1date: dt.datetime) -> None: ...
    @property
    def lots(self) -> list[DyeLotView]: ...
    @property
    def total_yds_prod(self) -> float: ...
    def total_yds_by(self, date: dt.datetime) -> float: ...
    def assign(self, ports: list[PortLoad]) -> DyeLot: ...
    def unassign(self, lview: DyeLotView) -> DyeLotView: ...