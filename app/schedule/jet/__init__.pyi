from app.schedule.jet.jetsched import JetSched as JetSched

import datetime as dt
from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.schedule import Job

class Jet(HasID[str], SuperImmut):
    """
    A class for Jet objects. All attributes are frozen, but the sched object is (purposefully)
    mutable.
    """
    n_ports: int
    load_rng: FloatRange
    date_rng: DateRange
    sched: JetSched
    def __init__(self, id: str, n_ports: int, load_min: float, load_max: float,
                 min_date: dt.datetime, max_date: dt.datetime) -> None:
        """
        Initialize a new Jet object.

            id:
              This jet's id (as seen on the demand planning file).
            n_ports:
              The number of ports on this jet.
            load_min:
              The minimum pounds that can be loaded into one port on this jet.
            load_max:
              The maximum pounds that can be loaded into one port on this jet.
            min_date:
              The earliest date to schedule new jobs.
            max_date:
              The latest date to schedule new jobs.
        """
        ...
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
    @property
    def jobs(self) -> list[Job]:
        """The jobs currently scheduled to this jet."""
        ...
    def get_start_idx(self, job: Job) -> int:
        """
        Get the latest possible point in the schedule at which to insert the given Job in order to
        finish on time and maintain shade sequencing. Being on time is prioritized.

            job:
              The Job to be inserted.
        
        Returns an index at which to insert the new Job. If the job cannot be run on time, it returns
        -1.
        """
        ...
    def insert_job(self, job: Job, idx: int) -> tuple[JetSched, list[Job]]:
        """
        Create a new schedule, inserting 'job' at the provided 'idx'.

            job:
              The Job to be inserted.
            idx:
              The index at which to insert the new Job.
        
        Returns a tuple containing the new schedule and any jobs that were "kicked out" due to the
        insertion.
        """
        ...