import datetime as dt
from app.support import HasID, SuperImmut
from app.style import Color
from app.schedule.dyelot import DyeLot

_CTR = 0

class Job(HasID[str], SuperImmut):
    """
    A class for Job objects.
    """
    color: Color
    cycle_time: dt.timedelta
    max_date: dt.datetime
    @classmethod
    def make_strip(cls, start: dt.datetime, id: str | None = None,
                   end_time: dt.datetime | None = None) -> 'Job':
        """
        Create a new Job object to represent a strip cycle. If 'id' and 'end_time' are None,
        they are created automatically. If one is not None, both must be passed explicitly.

            start:
              The start date and time of the strip cycle.
            id: (default None)
              If provided, the dyelot id from adaptive.
            end_time: (default None)
              If provided, the end date and time from adaptive.
        """
        ...
    @classmethod
    def make_empty_job(cls, start: dt.datetime, id: str, end_time: dt.datetime) -> 'Job':
        """
        Create a new Job object using data from adaptive. Since the item produced is unknown,
        the 'lots' attribute will be empty and a default Color object will be provided.

            start:
              The start date and time of the job from adaptive.
            id:
              The dyelot id from adaptive.
            end_time:
              The end date and time of the job from adaptive.
        """
        ...
    @classmethod
    def make_job(cls, start: dt.datetime, max_date: dt.datetime, lots: tuple[DyeLot, ...]) -> 'Job':
        """
        Create a new Job object using a tuple of DyeLots. The id will be created automatically,
        the color will come from the items in the lots, and the cycle time will be set based on
        the color.

            start:
              The start date and time of the job.
            max_date:
              The maximum date and time to which the job can be pushed while sorting.
            lots:
              The DyeLots that are part of the job.
        """
        ...
    def __init__(self, start: dt.datetime, max_date: dt.datetime, id: str,
                 lots: tuple[DyeLot, ...], clr: Color, cycle_time: dt.timedelta) -> None:
        """
        Initialize a new Job object.

            start:
              The start date and time of the job.
            max_date:
              The maximum date and time to which the job can be pushed while sorting.
            id:
              The unique id of this job.
            lots:
              The DyeLots that compose this job.
            clr:
              The Color of this job.
            cycle_time:
              The cycle time of this job.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
    @property
    def start(self) -> dt.datetime: ...
    @start.setter
    def start(self, new: dt.datetime) -> None: ...
    @property
    def end(self) -> dt.datetime: ...
    @property
    def lots(self) -> tuple[DyeLot, ...]: ...