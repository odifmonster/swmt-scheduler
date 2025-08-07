#!/usr/bin/env python

from typing import NewType, Literal

ShadeGrade = NewType('ShadeGrade', str)
SOLUTION = ShadeGrade('0_SOLUTION')
LIGHT = ShadeGrade('1_LIGHT')
MEDIUM = ShadeGrade('2_MEDIUM')
BLACK = ShadeGrade('3_BLACK')

type RawShadeInt = Literal[1, 2, 3, 4]
type RawShadeStr = Literal['LIGHT', 'MEDIUM', 'BLACK', 'SOLUTION']

def _get_shade_grade(raw: RawShadeInt | RawShadeStr):
    if type(raw) is int:
        match raw:
            case 1: return LIGHT
            case 2: return MEDIUM
            case 3: return BLACK
            case 4: return SOLUTION
            case _: raise ValueError(f'Unknown shade grade: {raw}')
    if type(raw) is str:
        match raw:
            case 'LIGHT': return LIGHT
            case 'MEDIUM': return MEDIUM
            case 'BLACK': return BLACK
            case 'SOLUTION': return SOLUTION
            case _: raise ValueError(f'Unknown shade grade: {repr(raw)}.')
    raise TypeError(f'\'raw\' argument must be type \'int\' or \'str\'.')

class _ColorBase:

    def __init__(self, name: str, number: int, shade: RawShadeInt | RawShadeStr):
        self.__name = name
        self.__number = number
        self.__shade = _get_shade_grade(shade)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def number(self):
        return f'{self.__number:05}'
    
    @property
    def shade(self):
        return self.__shade
    
    def __repr__(self):
        return repr(self.name)

class Color(_ColorBase):
    pass