from app.helper import HasID
from app.styles.color import ColorGrade as ColorGrade

class Color:
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
    def __init__(self, name: str, prefix: str) -> None: ...
    @property
    def name(self) -> str: ...

class Greige(Style):
    def __init__(self, name: str) -> None: ...

class FabricMaster(Style):
    def __init__(self, name: str) -> None: ...

class Fabric(Style):
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
    def greige(self) -> Greige:
        """The greige style used for this item."""
        ...
    @property
    def color(self) -> Color:
        """The color of this item."""
        ...
    @property
    def yds_per_lb(self) -> float:
        """The average yield (yards produced per pound of greige) for this item."""
        ...