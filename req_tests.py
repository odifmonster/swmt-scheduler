#!/usr/bin/env python

import unittest

import random, datetime as dt

from app.style import GreigeStyle, FabricStyle, Color
from app.schedule import Req, Demand

def random_str_id(length: int) -> str:
    digits = [str(i) for i in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

def make_greige_styles(n: int) -> list[GreigeStyle]:
    tgts = [(330, 370), (342.5, 382.5), (355, 395)]
    ret: list[GreigeStyle] = []
    for i in range(n):
        tgt = random.choice(tgts)
        ret.append(GreigeStyle(f'STYLE_{i+1:02}', tgt[0], tgt[1]))
    return ret

def make_colors(n: int) -> list[Color]:
    return [Color(f'COLOR_{i+1:02}', int(random_str_id(5)), random.randint(1,4)) for i in range(n)]

def make_fabric_styles(n: int, greiges: list[GreigeStyle], colors: list[Color]) -> list[FabricStyle]:
    ret: list[FabricStyle] = []
    masters = [f'MASTER_{i+1:02}' for i in range(15)]
    jets = [f'Jet-{i:02}' for i in (1,2,3,4,7,8,9,10)]
    for i in range(n):
        fab = FabricStyle(f'STYLE_{i+1:02}', random.choice(greiges), random.choice(masters),
                          random.choice(colors), 2.2+random.random()*0.6, jets)
        ret.append(fab)
    return ret

class TestReq(unittest.TestCase):

    def setUp(self):
        self.greiges = make_greige_styles(10)
        self.colors = make_colors(20)
        self.items = make_fabric_styles(100, self.greiges, self.colors)
    
    """
    Tests to run:

        1.  Req initializer argument validation

            You are allowed to pass in a 'subscriber' requirement to the Req initializer. This is to
            reflect the fact that requirements on the same item with different due dates can be
            fulfilled with one job. The initializer should throw ValueErrors in the following cases:

            a.  The current Req and the subscriber Req have different fabric items
                msg='Cannot subscribe requirement for item <repr(subscriber.item)> to requirement for item <repr(cur_item)>.'
                Where 'subscriber' is some Req object and 'cur_item' is the FabricStyle for the new Req object.

            b.  The current Req has a due date equal to or later than that of the subscriber Req
                msg='Subscribed requirements must have later due dates than their notifiers.'
        
        2.  Chain of subscribed Reqs updates correctly on single call

            Suppose you had a series of requirements initialized like so:
              req3 = Req(yds=2000, ...)
              req2 = Req(yds=100, ..., subscriber=req3)
              req1 = Req(yds=1000, ..., subscriber=req2)

            If you call req1.fulfill(amount) where amount*item.yld > req1.yds, you should see that
            reflected in both req2 and req3.
            If req1.yds < amount*item.yld < req1.yds+req2.yds, then after calling req1.fulfill(amount):
              req1.yds = old_req1_yds - amount*item.yld
              req2.yds = old_req2_yds - abs(req1.yds)
              req3.yds is unchanged
            if amount*item.yld > req1.yds+req2.yds, then:
              req1.yds = old_req1_yds - amount*item.yld
              req2.yds = old_req2_yds - abs(req1.yds)
              req3.yds = old_req3_yds - abs(req2.yds)

        3.  Chain of subscribed Reqs updates correctly on multiple calls

            Given a similar setup to (2), test the behavior for the following cases:
                a. Calling req1.fulfill(amount1) and req1.fulfill(amount2) where amount1 is less
                   than req1 and amount1+amount2 > req1
                b. Calling req1.fulfill(amount1) and req1.fulfill(amount2) where amount1 > req1

        4.  Req updates allowed inside of Demand object

            Use a similar setup to (2), create a Demand object, and add the Req objects to it.
            If you remove the Req at the top of the chain, confirm that calling 'fulfill' on large
            amounts updates the other Req objects in the group.
    """