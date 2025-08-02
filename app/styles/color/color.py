#!/usr/bin/env python

from app.support import HasID
from .dye_grade import DyeGrade

class Color(HasID[str]):

    def __init__(self, id, name, grade):
        super().__init__(id, 'COLOR')

        self.__name = name
        self.__grade = DyeGrade(grade)

    @property
    def number(self):
        return self.id
    
    @property
    def name(self):
        return self.__name
    
    @property
    def grade(self):
        return self.__grade