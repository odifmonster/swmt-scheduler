from app.materials.roll.roll import SizeClass as SizeClass, LARGE as LARGE, NORMAL as NORMAL, \
    SMALL as SMALL, HALF as HALF, PARTIAL as PARTIAL

from app.support.grouped import Data, DataView
from app.support import SuperImmut
from app.style import GreigeStyle

class RollAlloc(SuperImmut, attrs=('roll_id','lbs'), frozen=('roll_id','lbs')):
    """Simple class for representing an allocation of a piece of one roll."""
    roll_id: str
    lbs: float
    def __init__(self, roll_id: str, lbs: float) -> None: ...

class Roll(Data[str], mod_in_group=False, attrs=('item','size','lbs'),
           priv_attrs=('init_wt','cur_wt','allocs'), frozen=('*init_wt','item')):
    """
    A class for Roll objects.
    """
    item: GreigeStyle
    def __init__(self, id: str, item: GreigeStyle, lbs: float) -> None:
        """
        Initialize a new Roll object.

            id:
              The id of this roll in inventory.
            item:
              The greige style of this roll.
            lbs:
              The weight of this roll.
        """
        ...
    @property
    def lbs(self) -> float:
        """The current weight of this roll."""
        ...
    @property
    def size(self) -> SizeClass:
        """The size of this roll relative to the standard for this item."""
        ...
    def allocate(self, lbs: float) -> RollAlloc:
        """
        Allocate a piece of this roll. Returns the RollAlloc object representing the used portion.
        """
        ...
    def deallocate(self, piece: RollAlloc) -> None:
        """
        Deallocate a piece of this roll. Must be an object returned by this Roll's 'allocate'
        method.
        """
        ...
    def view(self) -> RollView: ...

class RollView(DataView[str], attrs=('item','size','lbs'), funcs=('allocate','deallocate'),
               dunders=('repr',)):
    item: GreigeStyle
    def __init__(self, link: Roll) -> None: ...
    @property
    def lbs(self) -> float:
        """The current weight of this roll."""
        ...
    @property
    def size(self) -> SizeClass:
        """The size of this roll relative to the standard for this item."""
        ...
    def allocate(self, lbs: float) -> RollAlloc:
        """
        Allocate a piece of this roll. Returns the RollAlloc object representing the used portion.
        """
        ...
    def deallocate(self, piece: RollAlloc) -> None:
        """
        Deallocate a piece of this roll. Must be an object returned by this Roll's 'allocate'
        method.
        """
        ...