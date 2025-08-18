#!/usr/bin/env python

from typing import TypedDict, Unpack

from app.groups import GroupedView, Grouped
from app.style import GreigeStyle
from ..roll import Roll, SizeClass

class StyleProps(TypedDict):
    greige: GreigeStyle

class SizeProps(StyleProps):
    size: SizeClass

class RSizeView(GroupedView[str, str]):
    pass

class RSizeGroup(Grouped[str, str]):

    def __init__(self, **kwargs: Unpack[SizeProps]):
        super().__init__(RSizeView(self), 'id', **kwargs)

    def make_group(self, data: Roll, prev_props: SizeProps):
        return self.make_atom(data, 'greige', 'size', 'id')
    
class RStyleView(GroupedView[str, SizeClass]):
    pass

class RStyleGroup(Grouped[str, SizeClass]):

    def __init__(self, **kwargs: Unpack[StyleProps]):
        super().__init__(RSizeView(self), 'size', 'id', **kwargs)

    def make_group(self, data: Roll, prev_props: StyleProps):
        return RSizeGroup(size=data.size, **prev_props)
    
class InvView(GroupedView[str, GreigeStyle]):
    pass

class Inventory(Grouped[str, GreigeStyle]):

    def __init__(self):
        super().__init__(InvView(self), 'greige', 'size', 'id')

    def make_group(self, data: Roll, prev_props):
        return RStyleGroup(greige=data.greige)