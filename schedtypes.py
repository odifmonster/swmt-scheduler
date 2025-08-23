#!/usr/bin/env python

from typing import NamedTuple

from app.inventory import RollView
from app.schedule import Jet

class RollPiece(NamedTuple):
    id: str
    rview: RollView
    lbs: float

class PortLoad(NamedTuple):
    roll1: RollPiece
    roll2: RollPiece | None

class SplitRoll(NamedTuple):
    full: list[RollPiece]
    extra: RollPiece

class NewJobInfo(NamedTuple):
    jet: Jet
    idx: int
    port_loads: list[PortLoad]
    cost: float