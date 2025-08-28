#!/usr/bin/env python

from ...dyelot import DyeLot
from datetime import datetime

_CTR = 20

class Job:
    def __init__(self, dyelots: list[DyeLot], start: datetime, idx = None):
        self.id = ""

        for dyelot in dyelots:
            self.id += dyelot.id

        if idx:
            if idx >= 0:
                self.id+= f"@{idx}"
            else:
                globals()['_CTR'] += 1
                self.id += f'@{globals()['_CTR']}'

        self.lots = dyelots
        self.start = start
        self.end = start + self.lots[0].cycle_time
        
        self.greige = self.lots[0].greige
        self.color = self.lots[0].color
        self.shade = self.lots[0].shade

    def activate(self):
        for lot in self.lots:
            lot.start = self.start
        
    def deactivate(self):
        for lot in self.lots:
            lot.start = None


