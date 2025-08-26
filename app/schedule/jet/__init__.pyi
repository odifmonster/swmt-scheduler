from app.schedule.jet.job import Job as Job
from app.schedule.jet.jetsched import JetSched as JetSched

import datetime as dt
from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.schedule import DyeLot

class Jet(HasID[str], SuperImmut,
          attrs=('_prefix','id','n_ports','load_rng','date_rng','jobs'),
          priv_attrs=('id','init_sched','cur_sched'),
          frozen=('*id','*init_sched','n_ports','load_rng','date_rng')):
    n_ports: int
    load_rng: FloatRange
    date_rng: DateRange
    def __init__(self, id: str, n_ports: int, min_load: float, max_load: float,
                 start: dt.datetime, end: dt.datetime) -> None: ...
    @property
    def jobs(self) -> tuple[Job, ...]: ...
    def add_adaptive_job(self, job: Job) -> None: ...
    def init_new_sched(self) -> None: ...
    def insert(self, lots: tuple[DyeLot, ...]) -> tuple[JetSched | None, list[Job]]: ...
    def set_sched(self, sched: JetSched) -> JetSched: ...