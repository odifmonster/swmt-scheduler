from app.schedule.jet.job import Job as Job
from app.schedule.jet.jetsched import JetSched as JetSched

import datetime as dt
from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.support.logging import HasLogger
from app.schedule import DyeLot

class Jet(HasLogger, HasID[str], SuperImmut,
          attrs=('_logger','_prefix','id','logger','n_ports','load_rng','date_rng',
                 'jobs','n_new_jobs','cur_sched'),
          priv_attrs=('id','init_sched','cur_sched'),
          frozen=('*id','*init_sched','n_ports','load_rng','date_rng')):
    """
    A class for Jet objects. They have frozen 'n_ports',
    'load_rng', and 'date_rng' attributes.
    """
    n_ports: int # the number of ports on this jet
    load_rng: FloatRange # the range of weights one port will accept
    date_rng: DateRange # the range of dates this jet's schedule should cover
    def __init__(self, id: str, n_ports: int, min_load: float, max_load: float,
                 start: dt.datetime, end: dt.datetime) -> None:
        """
        Initialize a new Jet object.

            id:
              This machine's id.
            n_ports:
              The number of ports on this jet.
            min_load:
              The minimum number of pounds to load a port with.
            max_load:
              The maximum number of pounds to load a port with.
            start:
              The earliest date to schedule a new job.
            end:
              The latest date to schedule a new job.
        """
        ...
    @property
    def jobs(self) -> tuple[Job, ...]:
        """All the jobs currently scheduled to this jet."""
        ...
    @property
    def n_new_jobs(self) -> int:
        """The number of new, non-strip jobs scheduled to this jet."""
        ...
    @property
    def cur_sched(self) -> JetSched: ...
    def add_adaptive_job(self, job: Job) -> None:
        """Directly adds the provided job object to the initial schedule."""
        ...
    def init_new_sched(self) -> None:
        """Initializes a new schedule, passing in the adaptive schedule as the previous one."""
        ...
    def get_start_idx(self, lots: tuple[DyeLot, ...], due_date: dt.datetime) -> int: ...
    def insert(self, lots: tuple[DyeLot, ...], idx: int) -> tuple[JetSched | None, list[Job]]:
        """
        Tries to insert a job with the given lots at the given
        index in the schedule.

            lots:
              The dyelots that will go in the new job.
            idx:
              The index at which to insert the new job.
        
        Returns the new JetSched if there is space and None otherwise
        and a list of the new jobs created by the insertion.
        """
        ...
    def set_sched(self, sched: JetSched) -> JetSched:
        """
        Sets the current schedule to the provided JetSched and
        activates it. Deactivates the previous schedule and
        returns it.
        """
        ...

def init(start: dt.datetime, end: dt.datetime) -> None:
    """
    Initialize necessary components of app.schedule.jet sub-module.
    You must run this function before using this sub-module.

        start:
          The starting date to use for scheduling new jobs.
    """
    ...

def get_jets() -> list[Jet]: ...

def get_by_alt_id(id: str) -> Jet | None: ...