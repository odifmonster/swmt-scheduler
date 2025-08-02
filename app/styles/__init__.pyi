from app.styles.fabric import FabricMaster as FabricMaster

from typing import NamedTuple, Literal, Self
from app.support import HasID

class Style(HasID[str]):
    """
    A base class for styles. Mostly for aesthetic purposes.
    """
    def __init__(self, id: str, prefix: str) -> None: ...
    @property
    def name(self) -> str: ...

class WeightRange(NamedTuple):
    min: float
    max: float
    avg: float

class Greige(Style):
    """
    A class for storing information about a greige style (NOT for greige rolls).
    Includes the style name and the standard weight range
    """
    def __init__(self, id: str, std_wt: float) -> None: ...
    @property
    def roll_range(self) -> WeightRange:
        """Standard weight range for a roll in this style."""
        ...
    @property
    def port_range(self) -> WeightRange:
        """Standard weight range for a port containing this style."""
        ...
    def __str__(self) -> str: ...

class DyeGrade:
    """
    A class for dye/shade 'grades'. Ordering is SOLUTION < LIGHT < MEDIUM < BLACK.
    """
    def __init__(self, val: Literal['LIGHT', 'MEDIUM', 'BLACK', 'SOLUTION'] | Literal[1, 2, 3, 4]) -> None: ...
    def __str__(self) -> str: ...
    def __eq__(self, value: Self) -> bool: ...
    def __lt__(self, value: Self) -> bool: ...

class Color(HasID[str]):
    """
    A class for fabric item colors. Stores number, name, and dye/shade grade.
    Color number used has id.
    """
    def __init__(self, id: str, name: str,
                 grade: Literal['LIGHT', 'MEDIUM', 'BLACK', 'SOLUTION'] | Literal[1, 2, 3, 4]) -> None: ...
    @property
    def number(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def grade(self) -> DyeGrade: ...

class Fabric(Style):
    """
    A class for fabric styles (i.e. items). Stores the full finished item number,
    as well as the master style, the color, greige style, and average yield (yards per pound).
    """
    def __init__(self, id: str, greige: Greige,
                 master: str, color: Color, yld: float) -> None: ...
    @property
    def greige(self) -> Greige: ...
    @property
    def master(self) -> FabricMaster: ...
    @property
    def color(self) -> Color: ...
    @property
    def yds_per_lb(self) -> float: ...
    def __str__(self) -> str: ...