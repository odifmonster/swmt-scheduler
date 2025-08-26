import datetime as dt
from app.support import HasID, SuperImmut, DateRange
from app.style import FabricStyle, GreigeStyle
from app.materials import PortLoad
from app.schedule import DyeLot
from app.schedule.jet import Job

class JetSched(HasID[int], SuperImmut,
               attrs=('_prefix','id','soil_level','jobs_since_strip','rem_time',
                      'last_job_end','jobs'),
               priv_attrs=('id','init_sched','soil','jss','date_rng','jobs'),
               frozen=('*id','*init_sched','*date_rng')):
    """
    A class for JetSched objects. Represents one version of a schedule
    on a jet. Schedules can only be added to.
    """
    def __init__(self, date_rng: DateRange, prev_sched: 'JetSched | None' = None) -> None:
        """
        Initialize a new JetSched object.

            date_rng:
              The range of dates new jobs can be scheduled in.
            prev_sched: (default None)
              The schedule before this one on a jet. Represents the jobs
              already scheduled to the jet on adaptive.
        """
        ...
    @property
    def soil_level(self) -> int:
        """The soil level of the jet after running this schedule."""
        ...
    @property
    def jobs_since_strip(self) -> int:
        """The number of jobs run since the last strip cycle."""
        ...
    @property
    def last_job_end(self) -> dt.datetime:
        """
        The end date and time of the last job in this schedule.
        Skips weekends as necessary.
        """
        ...
    @property
    def rem_time(self) -> dt.timedelta:
        """The remaining time available for new jobs on this schedule."""
        ...
    @property
    def jobs(self) -> tuple[Job, ...]:
        """The jobs in this schedule."""
        ...
    def copy(self) -> JetSched:
        """Return a new JetSched object with the same initial values as this one."""
        ...
    def get_needed_strip(self, item: FabricStyle) -> FabricStyle | None:
        """Get the strip required (if any) before running the given item."""
        ...
    def can_add(self, lots: tuple[DyeLot, ...]) -> bool:
        """Returns True iff there is space in the schedule to run the given lots as a job."""
        ...
    def add_job(self, job: Job) -> None:
        """Adds the given job to the end of the schedule."""
        ...
    def add_lots(self, lots: tuple[DyeLot, ...]) -> Job:
        """Creates a job object from the provided lots, adds them to the schedule, and returns the job."""
        ...
    def activate(self) -> None:
        """Activate all the jobs in this schedule."""
        ...
    def deactivate(self) -> None:
        """Deactivate all the jobs in this schedule."""
        ...
    def free_greige(self) -> dict[GreigeStyle, list[PortLoad]]:
        """
        Get any additional greige that is available from the lots in this
        schedule (if deactivated). Returns a dictionary mapping greige
        styles to released port loads.
        """
        ...