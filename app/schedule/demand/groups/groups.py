#!/usr/bin/env python

from typing import TypedDict, Unpack
import datetime

from app.support import PrettyArgsOpt
from app.support.groups import Grouped, GroupedView
from app.style import GreigeStyle

class ColorProps(TypedDict):
    due_date: datetime.datetime
    greige: GreigeStyle
    color_num: str

class ColorGroupView(GroupedView[int, PrettyArgsOpt, int],
                     no_access=['add','remove'],
                     overrides=[],
                     dunders=['eq','hash']):
    pass

class ColorGroup(Grouped[int, PrettyArgsOpt, int]):
    
    def __init__(self, **props: Unpack[ColorProps]):
        super().__init__('id', **props)

class GreigeProps(TypedDict):
    due_date: datetime.datetime
    greige: GreigeStyle

class GreigeGroupView(GroupedView[int, PrettyArgsOpt, str, int],
                      no_access=['add','remove'],
                      overrides=[],
                      dunders=['eq','hash']):
    pass

class GreigeGroup(Grouped[int, PrettyArgsOpt, str, int]):

    def __init__(self, **props: Unpack[GreigeProps]):
        super().__init__('color_num', 'id', **props)

class PriorityProps(TypedDict):
    due_date: datetime.datetime

class PriorityGroupView(GroupedView[int, PrettyArgsOpt, GreigeStyle, str, int],
                        no_access=['add','remove'],
                        overrides=[],
                        dunders=['eq','hash']):
    pass

class PriorityGroup(Grouped[int, PrettyArgsOpt, GreigeStyle, str, int]):

    def __init__(self, **props: Unpack[PriorityProps]):
        super().__init__('greige', 'color_num', 'id', **props)

class DemandGroupView(GroupedView[int, PrettyArgsOpt, datetime.datetime, GreigeStyle, str, int],
                      no_access=['add','remove'],
                      overrides=[],
                      dunders=['eq','hash']):
    pass

class DemandGroup(Grouped[int, PrettyArgsOpt, datetime.datetime, GreigeStyle, str, int]):

    def __init__(self):
        super().__init__('due_date', 'greige', 'color_num', 'id')