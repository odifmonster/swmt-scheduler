#!/usr/bin/env python

import datetime as dt

from app.support.grouped import Grouped, GroupedView, Atom
from app.style import Color, GreigeStyle
from .order import Order, OrderView

class ColorGroup(Grouped[str, str]):

    def __init__(self, **kwargs):
        super().__init__(ColorView(self), 'id', **kwargs)

    def make_group(self, data, **kwargs):
        return Atom[str](data, 'due_date', 'greige', 'color', 'id')

class ColorView(GroupedView[str, str]):
    pass

class GreigeGroup(Grouped[str, Color]):
    
    def __init__(self, **kwargs):
        super().__init__(GreigeView(self), 'color', 'id', **kwargs)

    def make_group(self, data, **kwargs):
        return ColorGroup(color=data.color, **kwargs)

class GreigeView(GroupedView[str, Color]):
    pass

class DateGroup(Grouped[str, GreigeStyle]):

    def __init__(self, **kwargs):
        super().__init__(DateView(self), 'greige', 'color', 'id', **kwargs)

    def make_group(self, data, **kwargs):
        return GreigeGroup(greige=data.greige, **kwargs)

class DateView(GroupedView[str, GreigeStyle]):
    pass

class Demand(Grouped[str, dt.datetime]):

    def __init__(self):
        super().__init__(DemandView(self), 'due_date', 'greige', 'color', 'id')

    def make_group(self, data, **kwargs):
        return DateGroup(due_date=data.due_date)
    
    def get_matches(self, order: Order):
        ret: list[OrderView] = []
        dates = sorted(self)
        for date in dates:
            if order.greige not in self[date]: continue
            if order.color not in self[date, order.greige]: continue

            ret += list(self[date, order.greige, order.color].itervalues())
        return ret

class DemandView(GroupedView[str, dt.datetime]):
    pass