from app.helper import HasID
from app.styles.color import ColorGrade as ColorGrade

class Color:
    """A read-only type for handling information related to item color."""

    def __init__(self, name: str, num: str, grade: ColorGrade) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def number(self) -> str: ...
    @property
    def grade(self) -> ColorGrade:
        """The "grade" of this color (light, medium, black, or solution)."""
        ...

class Style(HasID[str]):
    """A read-only type for handling styles, mostly a readability thing."""
    def __init__(self, name: str, prefix: str) -> None: ...
    @property
    def name(self) -> str: ...

class Greige(Style):
    """A read-only type for handling greige style information."""
    def __init__(self, name: str) -> None: ...
    @property
    def roll_range(self) -> tuple[float, float]:
        """The standard weight range for a roll in this style."""
        ...
    @property
    def port_range(self) -> tuple[float, float]:
        """The standard weight range to load a port with this style."""
        ...

class FabricMaster(Style):
    def __init__(self, name: str) -> None: ...

class Fabric(Style):
    """A read-only type for handling fabric item information."""
    def __init__(self,
                 name: str,
                 master: FabricMaster,
                 greige: Greige,
                 color: Color,
                 yld: float) -> None: ...
    @property
    def master(self) -> FabricMaster:
        """The master style associated with this item."""
        ...
    @property
    def greige(self) -> Greige: ...
    @property
    def color(self) -> Color: ...
    @property
    def yds_per_lb(self) -> float: ...