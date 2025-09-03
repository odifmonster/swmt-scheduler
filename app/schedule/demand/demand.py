#!/usr/bin/env python

import datetime as dt

from app.support.grouped import Grouped, GroupedView, Atom
from app.support.logging import HasLogger, Logger, ProcessDesc, FailedYield, logged_generator
from app.style import Color, GreigeStyle
from .order import Order, OrderView

def matches_args(slf, order: Order) -> ProcessDesc:
    return {
        'desc1': f'Getting all orders that can be combined with {order}',
        'desc2': f'current order lbs={order.total_lbs:.2f}'
    }

def matches_yld(res: OrderView) -> ProcessDesc:
    return {
        'desc1': f'Combining with {res}', 'desc2': f'other order lbs={res.total_lbs:.2f}'
    }

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

class Demand(HasLogger, Grouped[str, dt.datetime], attrs=('_logger','logger')):

    _logger = Logger()

    @classmethod
    def set_logger(cls, lgr):
        cls._logger = lgr

    def __init__(self):
        Grouped.__init__(self, DemandView(self), 'due_date', 'greige', 'color', 'id')

    @property
    def logger(self):
        return type(self)._logger

    def make_group(self, data, **kwargs):
        return DateGroup(due_date=data.due_date)
    
    @logged_generator(matches_args, matches_yld)
    def get_matches(self, order: Order):
        dates = sorted(self)
        for date in dates:
            if order.greige not in self[date]: continue
            if order.color not in self[date, order.greige]: continue

            for view in self[date, order.greige, order.color].itervalues():
                match: OrderView = view
                if match.total_lbs <= 0: continue
                if match.item == order.item: continue
                total_lbs = order.total_lbs + match.total_lbs
                needed_ports = total_lbs / order.greige.port_rng.average()
                if needed_ports > 8:
                    yield FailedYield(desc1='Combined pounds exceeds maximum jet size',
                                      desc2=f'combined pounds={total_lbs:.2f}',
                                      desc3=f'minimum ports needed={needed_ports:.1f}')
                else:
                    yield match

class DemandView(GroupedView[str, dt.datetime]):
    pass