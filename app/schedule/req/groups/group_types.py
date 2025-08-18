#!/usr/bin/env python

from typing import TypedDict, Unpack
import datetime as dt

from app.groups import GroupedView, Grouped
from app.style import GreigeStyle, FabricStyle, Color
from ..req import Req

class GreigeProps(TypedDict):
    greige: GreigeStyle

class ColorProps(GreigeProps):
    color: Color

class ItemProps(ColorProps):
    item: FabricStyle

class PriorProps(ItemProps):
    due_date: dt.datetime

class ReqPriorView(GroupedView[str, str]):
    pass

class ReqPriorGroup(Grouped[str, str]):

    def __init__(self, **kwargs: Unpack[PriorProps]):
        super().__init__(ReqPriorView(self), 'id', **kwargs)

    def make_group(self, data: Req, prev_props: PriorProps):
        return self.make_atom(data, 'greige', 'color', 'item', 'due_date', 'id')
    
class ReqItemView(GroupedView[str, dt.datetime]):
    pass

class ReqItemGroup(Grouped[str, dt.datetime]):

    def __init__(self, **kwargs: Unpack[ItemProps]):
        super().__init__(ReqItemView(self), 'due_date', 'id', **kwargs)
    
    def make_group(self, data: Req, prev_props: ItemProps):
        return ReqPriorGroup(due_date=data.due_date, **prev_props)

class ReqColorView(GroupedView[str, FabricStyle]):
    pass

class ReqColorGroup(Grouped[str, FabricStyle]):

    def __init__(self, **kwargs: Unpack[ColorProps]):
        super().__init__(ReqColorView(self), 'item', 'due_date', 'id', **kwargs)

    def make_group(self, data: Req, prev_props: ColorProps):
        return ReqItemGroup(item=data.item, **prev_props)

class ReqGreigeView(GroupedView[str, Color]):
    pass

class ReqGreigeGroup(Grouped[str, Color]):

    def __init__(self, **kwargs: Unpack[GreigeProps]):
        super().__init__(ReqGreigeView(self), 'color', 'item', 'due_date', 'id', **kwargs)

    def make_group(self, data: Req, prev_props: GreigeProps):
        return ReqColorGroup(color=data.color, **prev_props)

class DemandView(GroupedView[str, GreigeStyle]):
    pass

class Demand(Grouped[str, GreigeStyle]):

    def __init__(self):
        super().__init__(DemandView(self), 'greige', 'color', 'item', 'due_date', 'id')
    
    def make_group(self, data: Req, prev_props):
        return ReqGreigeGroup(greige=data.greige)