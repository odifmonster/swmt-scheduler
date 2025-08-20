#!/usr/bin/env python

from typing import Literal

from app.inventory import Inventory, AllocRoll
from app.schedule import Req, ReqView, Jet, JetSched, Job

def cost_func(sched: JetSched, jet: Jet, reqs: set[ReqView]) -> float:
    return 1