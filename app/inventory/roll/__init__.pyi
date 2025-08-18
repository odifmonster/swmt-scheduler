from app.inventory.roll.roll import SizeClass as SizeClass, LARGE as LARGE, \
    NORMAL as NORMAL, SMALL as SMALL, HALF as HALF, PARTIAL as PARTIAL
from app.inventory.roll.alloc_roll import AllocPair as AllocPair

from app.support import HasID, SuperImmut
from app.groups import DataView, Data
from app.style import GreigeStyle

class AllocRoll(HasID[int], SuperImmut):
    """
    A class for allocated rolls. Allows you to combine up to two rolls to use up partials.
    Must be created from an existing Roll object.
    """
    greige: GreigeStyle
    def __init__(self, roll_id: str, greige: GreigeStyle, lbs: float) -> None:
        """
        Initialize a new AllocRoll object.

            roll_id:
              The id of the first Roll to allocate.
            greige:
              The greige style of the Roll object being used.
            lbs:
              The number of pounds to use from the given roll.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> int: ...
    @property
    def rolls(self) -> tuple[AllocPair] | tuple[AllocPair, AllocPair]:
        """
        The Roll or Rolls used to form this object, in the form of an id and a number of
        pounds.
        """
        ...
    @property
    def lbs(self) -> float: ...
    def __repr__(self) -> str: ...
    def add_roll(self, roll_id: str, lbs: float) -> None:
        """
        Allocates pounds from the given Roll to this object if possible. Will raise an error
        if this AllocRoll is already a combination of two rolls.

            roll_id:
              The id of the Roll to allocate.
            lbs:
              The number of pounds to use from the given roll.
        """
        ...

class RollView(DataView[str]):
    """
    A class for views of Roll objects.
    """
    greige: GreigeStyle
    def __init__(self, link: 'Roll') -> None: ...
    @property
    def lbs(self) -> float: ...
    @property
    def size(self) -> SizeClass: ...
    def __repr__(self) -> str: ...
    def use(self, lbs: float, aroll: AllocRoll | None = None, temp: bool = False) -> AllocRoll: ...
    def reset(self) -> None: ...
    def apply_changes(self) -> None: ...

class Roll(Data[str]):
    """
    A class for Roll objects. Refers to an actual roll in inventory. Allows you to temporarily
    allocate part or all of a roll and then subsequently reset or apply the temporary changes.
    """
    greige: GreigeStyle
    def __init__(self, id: str, greige: GreigeStyle, wt: float) -> None:
        """
        Initialize a new Roll object.

            id:
              The unique id of this roll (pulled from inventory file).
            greige:
              The greige style for this roll.
            wt:
              The initial pounds on this roll.
        """
        ...
    @property
    def lbs(self) -> float:
        """The weight of this roll, taking into account temporary changes."""
        ...
    @property
    def size(self) -> SizeClass:
        """The size of this roll relative to the target weight per roll in this style."""
        ...
    def __repr__(self) -> str: ...
    def use(self, lbs: float, aroll: AllocRoll | None = None,
            temp: bool = False) -> AllocRoll:
        """
        Allocate a number of pounds from this roll. Can specify temporary changes.

            lbs:
              The amount to allocate.
            aroll: (default None)
              The AllocRoll object to add the pounds to. If None, a new one will be created and
              returned.
            temp: (default False)
              When this flag is True, the changes will be temporary and can be reset later.
        """
        ...
    def reset(self) -> None:
        """
        Calling this method adds back any pounds temporarily allocated by the 'use' method.
        """
        ...
    def apply_changes(self) -> None:
        """
        Calling this method makes permanent any temporary changes to this roll's weight.
        """
        ...
    def view(self) -> RollView: ...