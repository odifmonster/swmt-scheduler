#!/usr/bin/env python

from abc import ABC, abstractmethod

from app.support import Viewable, HasID
from app.styles import Greige

class RollLike(ABC, HasID[str]):

    def __init__(self, id: str):
        print(id)
        super().__init__(id, 'GREIGE_ROLL')

    @property
    @abstractmethod
    def greige(self) -> Greige:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def weight(self) -> float:
        raise NotImplementedError()
    
    def __str__(self):
        ret = f'GREIGE_ROLL'
        ret += f'\n  [id=\'{self.id}\','
        ret += f'\n   style=\'{self.greige.name}\','
        ret += f'\n   weight={self.weight:.2f}]'
        return ret

class RollView(RollLike):

    def __init__(self, link: RollLike):
        super().__init__(link.id)

        self.__link = link
    
    @property
    def greige(self):
        return self.__link.greige
    
    @property
    def weight(self):
        return self.__link.weight
    
class Roll(RollLike):

    def __init__(self, id, greige, weight):
        RollLike.__init__(self, id)

        self.__greige = greige
        self.__weight = weight
        self.__view = RollView(self)

    @property
    def greige(self):
        return self.__greige
    
    @property
    def weight(self):
        return self.__weight
    
    def view(self):
        return self.__view
    
    def use(self, amount):
        if self.__weight < amount:
            raise ValueError(f'Desired amount exceeds remaining weight of roll.')
        self.__weight -= amount