#!/usr/bin/env python

from typing import NewType

from app.support import HasID, SuperImmut

ShadeGrade = NewType('ShadeGrade', str)
HEAVYSTRIP = ShadeGrade('0_HEAVYSTRIP')
STRIP = ShadeGrade('1_STRIP')
SOLUTION = ShadeGrade('2_SOLUTION')
LIGHT = ShadeGrade('3_LIGHT')
EMPTY = ShadeGrade('4_EMPTY')
MEDIUM = ShadeGrade('5_MEDIUM')
BLACK = ShadeGrade('6_BLACK')

def _get_shade_grade(rawval):
    if type(rawval) is str:
        match rawval:
            case 'HEAVYSTRIP': return HEAVYSTRIP
            case 'STRIP': return STRIP
            case 'SOLUTION': return SOLUTION
            case 'LIGHT': return LIGHT
            case 'EMPTY': return EMPTY
            case 'MEDIUM': return MEDIUM
            case 'BLACK': return BLACK
            case _:
                raise ValueError(f'Unknown shade: {repr(rawval)}')
    if type(rawval) is int:
        match rawval:
            case 1: return LIGHT
            case 2: return MEDIUM
            case 3: return BLACK
            case 4: return SOLUTION
            case 5: return EMPTY
            case 6: return STRIP
            case 7: return HEAVYSTRIP
            case _:
                raise ValueError(f'Unknown shade: {repr(rawval)}')
    raise TypeError(f'Invalid shade type: \'{type(rawval).__name__}\'')

class Color(HasID[str], SuperImmut, attrs=('_prefix','id','name','number','shade','soil'),
            frozen=('name','number','shade','soil')):
    
    def __init__(self, name, number, shade_val):
        shade = _get_shade_grade(shade_val)
        soil = 0
        if shade == HEAVYSTRIP:
            soil = -63
        elif shade == STRIP:
            soil = -27
        elif shade in (SOLUTION, LIGHT):
            soil = 1
        elif shade in (MEDIUM, EMPTY):
            soil = 3
        else:
            soil = 7
        SuperImmut.__init__(self, name=name, number=number, shade=shade, soil=soil)
    
    @property
    def _prefix(self):
        return 'Color'
    
    @property
    def id(self):
        return f'{self.number:05}'