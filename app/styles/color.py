#!/usr/bin/env python

from typing import Self

from enum import Enum, auto

class ColorGrade(Enum):
    LIGHT = auto()
    MEDIUM = auto()
    BLACK = auto()
    SOLUTION = auto()

    @classmethod
    def from_int(cls, val: int) -> Self:
        if val not in (1, 2, 3, 4):
            raise ValueError(f'Unrecognized color grade: {val}')
        
        match val:
            case 1: return cls.LIGHT
            case 2: return cls.MEDIUM
            case 3: return cls.BLACK
            case 4: return cls.SOLUTION

    def __str__(self) -> str:
        match self:
            case ColorGrade.LIGHT: return 'LIGHT'
            case ColorGrade.MEDIUM: return 'MEDIUM'
            case ColorGrade.BLACK: return 'BLACK'
            case ColorGrade.SOLUTION: return 'SOLUTION'
    
    def __eq__(self, value: Self) -> bool:
        return Enum.__eq__(self, value)
    
    def __lt__(self, value: Self) -> bool:
        match self:
            case ColorGrade.SOLUTION:
                return value != ColorGrade.SOLUTION
            case ColorGrade.LIGHT:
                return value in (ColorGrade.MEDIUM, ColorGrade.BLACK)
            case ColorGrade.MEDIUM:
                return value == ColorGrade.BLACK
            case ColorGrade.BLACK:
                return False

class Color:

    def __init__(self, name: str, num: str, grade: ColorGrade):
        self.__name = name
        self.__num = num
        self.__grade = grade

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def number(self) -> str:
        return self.__num
    
    @property
    def grade(self) -> ColorGrade:
        return self.__grade