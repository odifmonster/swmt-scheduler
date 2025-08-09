#!/usr/bin/env python

from typing import TypedDict, Unpack

from app.style import GreigeStyle
from app.support import PrettyArgsOpt
from app.support.groups import GroupedView, Grouped
from ..roll import SizeClass

class SizeProps(TypedDict):
    item: GreigeStyle
    size_class: SizeClass

class SizeGroupView(GroupedView[str, PrettyArgsOpt, str],
                    no_access=['add','remove'],
                    overrides=[],
                    dunders=['len','iter','contains','getitem']):
    pass

class SizeGroup(Grouped[str, PrettyArgsOpt, str]):
    
    def __init__(self, **props: Unpack[SizeProps]):
        super().__init__('id', **props)

class StyleProps(TypedDict):
    item: GreigeStyle

class StyleGroupView(GroupedView[str, PrettyArgsOpt, SizeClass, str],
                     no_access=['add','remove'],
                     overrides=[],
                     dunders=['len','iter','contains','getitem']):
    pass

class StyleGroup(Grouped[str, PrettyArgsOpt, SizeClass, str]):
    
    def __init__(self, **props: Unpack[StyleProps]):
        super().__init__('size_class', 'id', **props)

class InventoryView(GroupedView[str, PrettyArgsOpt, GreigeStyle, SizeClass, str],
                    no_access=['add','remove'],
                    overrides=[],
                    dunders=['len','iter','contains','getitem']):
    pass

class Inventory(Grouped[str, PrettyArgsOpt, GreigeStyle, SizeClass, str]):
    
    def __init__(self):
        super().__init__('item', 'size_class', 'id')