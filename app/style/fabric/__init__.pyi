from app.style.fabric.fabric import FabricMaster as FabricMaster, EMPTY as EMPTY

from app.support import HasID, SuperImmut
from app.style.greige import GreigeStyle
from app.style.color import Color

class FabricStyle(HasID[str], SuperImmut):
    """
    A class for fabric style information. All properties are immutable.
    """

    greige: GreigeStyle
    master: FabricMaster
    color: Color
    yld: float
    
    def __init__(self, item: str, greige: GreigeStyle, master: str,
                 color: Color, yld: float, allowed_jets: list[str]) -> None:
        """
        Initialize a new FabricStyle object.

            item:
              The style's item number. Becomes the object's id.
            greige:
              The fabric style's greige item.
            master:
              The master style.
            color:
              The fabric's color as a Color object.
            yld:
              The average yards yielded per pound of greige consumed.
            allowed_jets:
              The ids of the jets this item can run on.
        """
        ...
    def can_run_on_jet(self, jet_id: str) -> bool: ...

def init() -> None:
    """
    Initialize necessary components of app.style.fabric sub-module. You must run this
    function before using this sub-module.
    """
    ...

def get_fabric_style(id: str) -> GreigeStyle | None:
    """
    Returns the FabricStyle object with the given id, or None if it does not exist.
    """
    ...