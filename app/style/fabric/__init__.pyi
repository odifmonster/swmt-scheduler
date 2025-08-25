from app.style.fabric import color as color
from app.style.fabric.color import Color as Color

from app.support import HasID, SuperImmut
from app.style import GreigeStyle
from app.style.fabric.color import _RawShadeVal

class FabricStyle(HasID[str], SuperImmut, attrs=('_prefix','id','greige','color','yld'),
                  priv_attrs=('id','jets'), frozen=('*id','*jets','greige','color','yld')):
    """A class for FabricStyle objects. All attributes are immutable."""
    greige: GreigeStyle
    color: Color
    yld: float # yards yielded per pound of greige consumed
    def __init__(self, item: str, greige: GreigeStyle, clr_name: str, clr_num: int,
                 clr_shade: _RawShadeVal, yld: float, jets: list[str]) -> None:
        """
        Initialize a new FabricStyle object.

            item:
              The item number of this fabric.
            greige:
              The greige style this fabric uses.
            clr_name:
              The English name of this fabric's color.
            clr_num:
              The dye formula of this fabric's color as an int.
            clr_shade:
              A string or integer 1-7 indicating the color's shade.
              5-7 represent EMPTY, STRIP, and HEAVYSTRIP.
            yld:
              The yards of this fabric yielded per pound of greige
              consumed.
            jets:
              A list of ids of the jets this item can run on.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
    def can_run_on_jet(self, jet_id: str) -> bool:
        """
        Returns True iff this item can run on the jet with the given
        id.
        """
        ...
    def get_strip(self, soil_level: int) -> str | None:
        """
        Gets the kind of strip required (if any) to run this item on
        a jet with the provided soil level. Returns None if no strip
        is needed, otherwise returns the string id of the FabricStyle
        object representing the needed strip cycle.
        """
        ...

def init() -> None:
    """
    Initialize necessary components of app.style.fabric sub-module.
    You must run this function before using this sub-module.
    """
    ...

def get_style(id: str) -> FabricStyle | None:
    """
    Returns the FabricStyle object with the given id, or None if it does not exist.
    """
    ...