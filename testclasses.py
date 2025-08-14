#!/usr/bin/env python

from typing import TypedDict, Unpack
import random

from app.groups import DataView, Data, GroupedView, Grouped

class StyleProps(TypedDict):
    style: str

class SizeProps(StyleProps):
    weight: int

class RollView(DataView[str], dunders=['repr'], attrs=['style','weight']):
    style: str
    weight: int

class Roll(Data[str], dattrs=('style','weight'), dfrozen=('style',)):
    style: str
    weight: int

    def __init__(self, id: str, style: str, weight: int):
        rview = RollView(self)
        super().__init__(id, 'Roll', rview, style=style, weight=weight)

    def __repr__(self):
        return f'{self._prefix}(style={repr(self.style)}, wt={self.weight} lbs)'
    
    def view(self) -> RollView:
        return super().view()
    
class RSizeView(GroupedView[str, str]):
    
    def __init__(self, link: 'RSizeGroup') -> None:
        super().__init__(link)
    
class RSizeGroup(Grouped[str, str]):

    def __init__(self, **kwargs: Unpack[SizeProps]):
        view = RSizeView(self)
        super().__init__(view, 'id', **kwargs)

    def make_group(self, data: Roll, prev_props: SizeProps):
        return self.make_atom(data, 'style', 'weight', 'id')
    
    def remove(self, dview) -> Roll:
        return super().remove(dview)
    
    def view(self) -> RSizeView:
        return super().view()
    
class RStyleView(GroupedView[str, int]):

    def __init__(self, link: 'RStyleGroup') -> None:
        super().__init__(link)
    
class RStyleGroup(Grouped[str, int]):
    
    def __init__(self, **kwargs: Unpack[StyleProps]):
        view = RStyleView(self)
        super().__init__(view, 'weight', 'id', **kwargs)

    def make_group(self, data: Roll, prev_props: StyleProps) -> RSizeGroup:
        return RSizeGroup(weight=data.weight, **prev_props)
    
    def remove(self, dview) -> Roll:
        return super().remove(dview)
    
    def view(self) -> RStyleView:
        return super().view()
    
class RGroupView(GroupedView[str, str]):

    def __init__(self, link: 'RollGroup') -> None:
        super().__init__(link)
    
class RollGroup(Grouped[str, str]):

    def __init__(self):
        view = RGroupView(self)
        super().__init__(view, 'style', 'weight', 'id')

    def make_group(self, data: Roll, prev_props) -> RStyleGroup:
        return RStyleGroup(style=data.style)
    
    def remove(self, dview) -> Roll:
        return super().remove(dview)
    
    def view(self) -> RGroupView:
        return super().view()
    
def random_str_id(length: int) -> str:
    digits = [str(i) for i in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])
    
def main():
    styles = ['STYLE1', 'STYLE2', 'STYLE3']
    sizes = [300, 400]

    grp = RollGroup()
    for _ in range(100):
        grp.add(Roll(random_str_id(8), random.choice(styles), random.choice(sizes)))

    print(grp)

if __name__ == '__main__':
    main()