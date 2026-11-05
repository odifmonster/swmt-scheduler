#!/usr/bin/env python

from app.support import HasID, SuperImmut
from ...dyelot import DyeLot, DyeLotView
from ..order import Order

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','orders','lots','avg_use','hard_orders',
                 'safety_order'),
          priv_attrs=('id','lots'), frozen=('*id','item','orders','avg_use')):

    def __init__(self, item, buckets, safety=None):
        orders: list[Order] = []
        buckets = sorted(buckets, key=lambda b: b[0])
        total_yds = 0
        for pnum, due_date, yds in buckets:
            total_yds += yds
            if total_yds > 0:
                orders.append(Order(self, item, pnum, due_date, yds, total_yds))

        # average weekly use only counts the hard requirements
        avg_use = total_yds / (len(buckets)-1)

        # safety stock is a trailing bucket: it only needs to be produced
        # once every hard requirement has been covered
        if safety is not None:
            pnum, due_date, yds = safety
            if yds > 0:
                total_yds += yds
                orders.append(Order(self, item, pnum, due_date, yds, total_yds,
                                    safety=True))

        SuperImmut.__init__(self, priv={'id': item.id, 'lots': []}, item=item, orders=tuple(orders),
                            avg_use=avg_use)

    @property
    def _prefix(self):
        return 'Req'

    @property
    def id(self):
        return self.__id

    @property
    def lots(self) -> list[DyeLotView]:
        return list(map(lambda l: l.view(), self.__lots))

    @property
    def hard_orders(self) -> tuple[Order, ...]:
        return tuple(filter(lambda o: not o.safety, self.orders))

    @property
    def safety_order(self) -> Order | None:
        for o in self.orders:
            if o.safety:
                return o
        return None

    @property
    def total_yds_prod(self):
        return sum(map(lambda lview: lview.yds, filter(lambda lview: not lview.end is None, self.lots)))

    def total_yds_by(self, date):
        return sum(map(lambda lview: lview.yds,
                       filter(lambda lview: not lview.end is None and lview.end <= date, self.lots)))

    def assign(self, ports):
        newlot = DyeLot.new_lot(self.item, ports[0].greige, ports)
        self.__lots.append(newlot)
        return newlot

    def unassign(self, lview):
        lot = self.__lots.remove(lview)
        return lot
