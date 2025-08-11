from app.schedule.dyelot.allocation import Allocation as Allocation

from app.support import HasID
from app.style import FabricStyle
from app.inventory.roll import Roll
from app.schedule.demand import Demand, DemandView

class DyeLot(HasID[str]):
    """
    A class for DyeLot objects. Internally created dye lots use an auto-incremented
    id. Every DyeLot is assigned to exactly one Demand object.
    """
    def __init__(self, dmnd: Demand, int_id: int = -1): ...
    @property
    def dmnd(self) -> DemandView: ...
    @property
    def item(self) -> FabricStyle: ...
    @property
    def lbs(self) -> float: ...
    @property
    def yds(self) -> float: ...
    def __repr__(self) -> str: ...
    def assign_roll(self, roll: Roll, lbs: float) -> None:
        """
        Assign some pounds from the given roll to this DyeLot. 'lbs' can be less than
        the total number of pounds remaining in the roll.
        """
        ...
    def unassign_roll(self, roll: Roll) -> None: ...