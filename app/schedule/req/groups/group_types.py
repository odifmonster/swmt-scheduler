#!/usr/bin/env python

from typing import TypedDict, Unpack

from app.groups import GKeys, GroupedView, Grouped
from app.style import GreigeStyle, Color
from ..req import Req

type ReqColorKeys = GKeys[str, str]
type ReqGreigeKeys = GKeys[str, Color, str]
type DemandKeys = GKeys[str, GreigeStyle, Color, str]

class GreigeProps(TypedDict):
    greige: GreigeStyle

class ColorProps(GreigeProps):
    color: Color

class ReqColorView(GroupedView[str, str]):
    pass

class ReqColorGroup(Grouped[str, str]):

    def __init__(self, **kwargs: Unpack[ColorProps]):
        super().__init__(ReqColorView(self), 'id', **kwargs)

    def make_group(self, data: Req, prev_props: ColorProps):
        return self.make_atom(data, 'greige', 'color', 'id')
    
class ReqGreigeView(GroupedView[str, Color]):
    pass

class ReqGreigeGroup(Grouped[str, Color]):

    def __init__(self, **kwargs: Unpack[GreigeProps]):
        super().__init__(ReqGreigeView(self), 'color', 'id', **kwargs)

    def make_group(self, data: Req, prev_props: GreigeProps):
        return ReqColorGroup(color=data.color, **prev_props)
    
class DemandView(GroupedView[str, GreigeStyle]):
    pass

class Demand(Grouped[str, GreigeStyle]):

    def __init__(self):
        super().__init__(DemandView(self), 'greige', 'color', 'id')

    def make_group(self, data: Req, prev_props):
        return ReqGreigeGroup(greige=data.greige)