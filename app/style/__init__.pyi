from app.style import color as color
from app.style import translation as translation

from app.support import HasID, FloatRange

class GreigeStyle(HasID[str]):
    """
    A class for tracking information about greige styles.
    """
    def __init__(self, id: str, tgt_lbs: float) -> None:
        """
        Initialize a GreigeStyle object.
        id: the greige item number
        tgt_lbs: the standard pounds per port
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str:
        """The greige item number."""
        ...
    @property
    def port_range(self) -> FloatRange:
        """The standard range for pounds per port."""
        ...
    @property
    def roll_range(self) -> FloatRange:
        """The standard range for pounds per roll."""
        ...
    def __repr__(self) -> str: ...

class FabricStyle(HasID[str]):
    """
    A class for tracking information about fabric styles.
    """
    def __init__(self, id: str, greige: GreigeStyle, master: str,
                 clr: color.Color, yld: float) -> None:
        """
        Initialize a FabricStyle object.
        id: the fabric item number
        greige: the associated GreigeStyle
        master: the fabric master style
        clr: the associated Color
        yld: the average yards produced per pound of greige
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str:
        """The fabric item number."""
        ...
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def master(self) -> str: ...
    @property
    def color(self) -> color.Color: ...
    @property
    def yds_per_lb(self) -> float: ...
    def __repr__(self) -> str: ...