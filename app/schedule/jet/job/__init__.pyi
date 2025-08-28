import datetime as dt
from app.style import GreigeStyle, FabricStyle
from app.style.fabric.color import Color, ShadeGrade
from app.schedule import DyeLot

class Job:
    id: str
    lots: list[DyeLot]
    greige: GreigeStyle
    color: Color
    shade: ShadeGrade
    start: dt.datetime
    end: dt.datetime
    def __init__(self, dyelots: list[DyeLot], start: dt.datetime, idx: int | None = None) -> None: ...
    def activate(self) -> None: ...
    def deactivate(self) -> None: ...