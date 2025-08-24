#!/usr/bin/env python

from app.support.grouped import Atom, Grouped, GroupedView
from app.style import GreigeStyle
from app.materials.roll import SizeClass

class SizeGroup(Grouped[str, str]):

    def __init__(self, **kwargs):
        super().__init__(SizeView(self), 'id', **kwargs)
    
    def make_group(self, data, **kwargs):
        return Atom[str](data, 'item', 'size', 'id')
    
class SizeView(GroupedView[str, str]):
    pass

class StyleGroup(Grouped[str, SizeClass]):
    
    def __init__(self, **kwargs):
        super().__init__(StyleView(self), 'size', 'id', **kwargs)

    def make_group(self, data, **kwargs):
        return SizeGroup(size=data.size, **kwargs)

class StyleView(GroupedView[str, SizeClass]):
    pass

class Inventory(Grouped[str, GreigeStyle]):
    
    def __init__(self):
        super().__init__(InvView(self), 'item', 'size', 'id')

    def make_group(self, data, **kwargs):
        return StyleGroup(item=data.item)

class InvView(GroupedView[str, GreigeStyle]):
    pass