import datetime as dt
from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.schedule.jet.jetsched import JetSched as JetSched

class Jet(HasID[str], SuperImmut):
    n_ports: int
    load_rng: FloatRange
    date_rng: DateRange
    sched: JetSched
    def __init__(self, id: str, n_ports: int, load_min: float, load_max: float,
                 min_date: dt.datetime, max_date: dt.datetime) -> None: ...