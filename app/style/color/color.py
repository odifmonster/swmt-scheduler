#!/usr/bin/env python

from typing import NewType, Literal

from app.support import HasID, SuperImmut

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

class Color(HasID[str], SuperImmut,
            attrs=('_prefix','id','name','shade'),
            priv_attrs=('prefix','id')):
    
    def __init__(self, name: str, number: int, raw_shade: RawShadeInt | RawShadeStr):
        priv = { 'prefix': 'Color', 'id': number }
        super().__init__(priv, name=name, shade=_get_shade_grade(raw_shade))
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return f'{self.__id:05}'