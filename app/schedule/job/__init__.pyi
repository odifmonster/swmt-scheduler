from typing import overload
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
    @overload
    def __init__(self, start: dt.datetime, max_date: dt.datetime,
                 id = None, lots = None, cycle_time = None) -> None:
        """
        Initialize a new STRIP job.
        
            start:
              The start date and time.
            max_date:
              Should be start + 8 hours.
        """
        ...
    @overload
    def __init__(self, start: dt.datetime, max_date: dt.datetime,
                 id: str = ..., lots = None, cycle_time: dt.timedelta = ...) -> None:
        """
        Initialize a STRIP job with a known id and cycle_time
        
            start:
              The start date and time.
            max_date:
              Should be start + cycle_time.
            id:
              The Job id.
            cycle_time:
              The cycle time for this strip.
        """
        ...
    @overload
    def __init__(self, start: dt.datetime, max_date: dt.datetime,
                 id: str = ..., lots = tuple(), cycle_time: dt.timedelta = ...) -> None:
        """
        Initialize a job with a known id and cycle_time.
        
            start:
              The start date and time.
            max_date:
              Should be start + cycle_time.
            id:
              The Job id.
            cycle_time:
              The cycle time pulled from the Adaptive report.
        """
        ...
    @overload
    def __init__(self, start: dt.datetime, max_date: dt.datetime,
                 id = None, lots: tuple[DyeLot, ...] = ..., cycle_time = None) -> None:
        """
        Initialize a Job object using the created lots.
        
            start:
              The start date and time.
            max_date:
              The latest date and time this job can be pushed to when sorting jobs on a jet.
            lots:
              The DyeLots that are part of this job.
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