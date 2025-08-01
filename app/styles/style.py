#!/usr/bin/env python

from app.helper import HasID

class Style(HasID[str]):

    def __init__(self, name: str, prefix: str):
        HasID[str].__init__(self, name, prefix)

    @property
    def name(self) -> str:
        return self.id

class Greige(Style):

    def __init__(self, name: str, port_avg: float):
        Style.__init__(self, name, 'GREIGE STYLE')

        self.__avg_wt: float = port_avg
    
    @property
    def roll_range(self) -> tuple[float, float]:
        return ((self.__avg_wt-20)*2,(self.__avg_wt+20)*2)
    
    @property
    def port_range(self) -> tuple[float, float]:
        return (self.__avg_wt-20,self.__avg_wt+20)