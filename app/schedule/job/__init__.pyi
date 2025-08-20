import datetime as dt
from app.support import HasID, SuperImmut
from app.style import color
from app.schedule import DyeLot, DyeLotView

class Job(HasID[str], SuperImmut):
    """
    A class for Job objects. They can contain multiple DyeLots. Their starts are mutable, but all
    other attributes are frozen after initialization.
    """
    shade: color.ShadeGrade
    cycle_time: dt.timedelta
    @classmethod
    def make_job(cls, start: dt.datetime, lots: tuple[DyeLot, ...]) -> 'Job':
        """
        Create a new Job object using the provided lots.

            start:
              The start date and time for this job.
            lots:
              The DyeLots that compose this job. They will be used to set the item,
              which will in turn set the shade and cycle_time.
        
        Returns a Job object with the aformentioned properties.
        """
        ...
    @classmethod
    def make_placeholder(cls, id: str, start: dt.datetime, end: dt.datetime) -> 'Job':
        """
        Create a new Job object that represents an existing adaptive order.

            id:
              The dyelot id from adaptive.
            start:
              The start date and time from adaptive.
            end:
              The end date and time from adaptive.

        Returns a Job object with no lots. The cycle_time is computed from the start and end times.
        Since the item produced is unknown, the item and shade are both empty.
        """
        ...
    @classmethod
    def make_strip(cls, is_heavy: bool, start: dt.datetime, end: dt.datetime | None = None,
                   id: str | None = None) -> 'Job':
        """
        Create a new Job object representing a strip cycle. Can be from adaptive or automatic.

            is_heavy:
              A boolean flag for designating the new strip cycle as heavy. Should be False for
              all jobs from adaptive.
            start:
              The start date and time of the strip cycle.
            end: (default None)
              The end date and time of the strip cycle. If provided, it will be used to calculate
              the cycle time. The id must also be provided in this case. If None, the cycle time
              will come from the 'is_heavy' flag.
            id: (default None)
              The dyelot id from adaptive. If None, it will be automatically created. If provided,
              the 'end' argument must also be provided.
        
        Returns a Job object with no lots and a shade of STRIP or HEAVYSTRIP.
        """
        ...
    def __init__(self, id: str, shade: color.ShadeGrade, start: dt.datetime, cycle_time: dt.datetime,
                 lots: tuple[DyeLot, ...]) -> None:
        """
        Initialize a new Job object.

            id:
              This job's id.
            shade:
              The ShadeGrade of the dye formula used for this job. Can also be EMPTY, STRIP,
              or HEAVYSTRIP.
            start:
              The start date and time of this job. This will be used to set the start attribute
              of the provided DyeLots, if any.
            cycle_time:
              The cycle time of this job. This will be used to set the end attribute of the
              provided DyeLots, if any.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
    @property
    def start(self) -> dt.datetime:
        """The start date and time of this job."""
        ...
    @start.setter
    def start(self, new: dt.datetime) -> None: ...
    @property
    def end(self) -> dt.datetime:
        """The end date and time of this job."""
        ...
    @property
    def due_date(self) -> dt.datetime:
        """The earliest due date of any DyeLot in this job."""
        ...
    @property
    def lots(self) -> list[DyeLotView]:
        """The views of the lots that compose this job."""
        ...
    @property
    def yds(self) -> float:
        """The total yards this job will produce."""
        ...
    @property
    def lbs(self) -> float:
        """The total pounds this job will use."""
        ...