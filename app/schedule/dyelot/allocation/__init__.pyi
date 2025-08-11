from app.support import HasID
from app.inventory.roll import Roll, RollView

class Allocation(HasID[int]):
    """
    A class for allocations of rolls to dyelots. Once created, its attributes should
    not be changed.
    """
    def __init__(self, roll: Roll, lbs: float) -> None:
        """
        Initialize a new Allocation object. 'roll' is "used up" upon allocation.
        roll: the Roll to be allocated
        lbs: the number of pounds to allocate
        """
        ...
    @property
    def roll(self) -> RollView: ...
    @property
    def lbs(self) -> float: ...
    def __repr__(self) -> str: ...