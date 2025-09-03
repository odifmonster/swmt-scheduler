import datetime as dt
from app.support import HasID, SuperImmut, SuperView
from app.style import FabricStyle, GreigeStyle
from app.style.fabric.color import Color, ShadeGrade
from app.materials.inventory import PortLoad

class DyeLot(HasID[str], SuperImmut,
             attrs=('_prefix','id','ports','item','greige','shade','cycle_time',
                    'start','end','yds','lbs','min_date'),
             priv_attrs=('id','start','fin_time','view'),
             frozen=('*id','*fin_time','*view','ports','item','cycle_time',
                     'min_date')):
    """
    A class for DyeLot objects. Can be linked to multiple jobs
    for the purpose of comparing schedules. All attributes
    other than 'start' are immutable.
    """
    @classmethod
    def from_adaptive(cls, id: str, item: FabricStyle, start: dt.datetime,
                      end: dt.datetime) -> 'DyeLot':
        """
        Create a new DyeLot object using data from adaptive. The
        resulting object has a fabric style of EMPTY unless the
        provided 'id' is for a strip cycle.
        """
        ...
    @classmethod
    def new_strip(cls, item: FabricStyle, start: dt.datetime) -> 'DyeLot':
        """
        Create a new DyeLot object representing a strip cycle with
        the given start time. The item should be STRIP or HEAVYSTRIP.
        """
        ...
    @classmethod
    def new_lot(cls, item: FabricStyle, ports: list[PortLoad]) -> 'DyeLot':
        """
        Create a new DyeLot for a particular fabric item using the
        provided roll pieces.
        """
        ...
    ports: tuple[PortLoad, ...]
    item: FabricStyle
    cycle_time: dt.timedelta
    min_date: dt.datetime
    def __init__(self, id: str, ports: tuple[PortLoad, ...], item: FabricStyle,
                 start: dt.datetime | None, cycle_time: dt.timedelta,
                 fin_time: dt.timedelta, min_date: dt.datetime) -> None:
        """
        Initialize a new DyeLot object.

            id:
              The unique id of this DyeLot.
            ports:
              A tuple of PortLoad objects, containing the roll pieces
              allocated to this DyeLot.
            item:
              The item that will be produced by this lot.
            start:
              The start date for this lot, or None if it is not linked
              to a Job yet.
            cycle_time:
              The cycle time of this DyeLot. Should usually be the cycle
              time of the produced item.
            fin_time:
              The amount of time required to finish the item after
              dyeing.
        """
        ...
    def __repr__(self) -> str: ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style used for this DyeLot."""
        ...
    @property
    def color(self) -> Color:
        """The color of this DyeLot."""
        ...
    @property
    def shade(self) -> ShadeGrade:
        """The shade of this lot's color."""
        ...
    @property
    def start(self) -> dt.datetime | None:
        """The start time of this lot. If None, the lot has not been scheduled."""
        ...
    @start.setter
    def start(self, new: dt.datetime | None) -> None: ...
    @property
    def end(self) -> dt.datetime | None:
        """
        The date and time this lot will be available for shipping. If
        None, the lot has not been scheduled.
        """
        ...
    @property
    def yds(self) -> float:
        """The yards of fabric this lot will produce."""
        ...
    @property
    def lbs(self) -> float:
        """The pounds of greige this lot will consume."""
        ...
    def view(self) -> 'DyeLotView':
        """A live, read-only view of this object."""
        ...

class DyeLotView(SuperView[DyeLot],
                 attrs=('_prefix','id','ports','item','greige','shade','cycle_time',
                        'start','end','yds','lbs','min_date'),
                 dunders=('eq','hash','repr')):
    """A class for views of DyeLot objects."""
    ports: tuple[PortLoad, ...]
    item: FabricStyle
    cycle_time: dt.timedelta
    min_date: dt.datetime
    def __eq__(self, other: 'DyeLotView | DyeLot') -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    @property
    def greige(self) -> GreigeStyle:
        """The greige style used for this DyeLot."""
        ...
    @property
    def color(self) -> Color:
        """The color of this DyeLot."""
        ...
    @property
    def shade(self) -> ShadeGrade:
        """The shade of this lot's color."""
        ...
    @property
    def start(self) -> dt.datetime | None:
        """The start time of this lot. If None, the lot has not been scheduled."""
        ...
    @start.setter
    def start(self, new: dt.datetime | None) -> None: ...
    @property
    def end(self) -> dt.datetime | None:
        """
        The date and time this lot will be available for shipping. If
        None, the lot has not been scheduled.
        """
        ...
    @property
    def yds(self) -> float:
        """The yards of fabric this lot will produce."""
        ...
    @property
    def lbs(self) -> float:
        """The pounds of greige this lot will consume."""
        ...