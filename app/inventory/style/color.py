#!/usr/bin/env python

from typing import Self

from enum import Enum

class DyeType(Enum):

    LIGHT, MED, DARK, BLACK = 0, 1, 2, 3

    @classmethod
    def from_string(cls, val: str) -> Self:
        match val:
            case 'LIGHT': return cls.LIGHT
            case 'MEDIUM': return cls.MED
            case 'DARK': return cls.DARK
            case 'BLACK': return cls.BLACK
            case _:
                raise ValueError(f'Invalid DyeType name \'{val}\'')
    
    def __lt__(self, other: Self) -> bool:
        match self:
            case DyeType.LIGHT:
                return other != DyeType.LIGHT
            case DyeType.MED:
                return other in (DyeType.DARK, DyeType.BLACK)
            case DyeType.DARK:
                return other == DyeType.BLACK
            case DyeType.BLACK:
                return False
    
    def __str__(self) -> str:
        match self:
            case DyeType.LIGHT:
                return 'LIGHT'
            case DyeType.MED:
                return 'MEDIUM'
            case DyeType.DARK:
                return 'DARK'
            case DyeType.BLACK:
                return 'BLACK'

class _ColorBase:

    def __init__(self, num: str, name: str, dye_type: str):
        self.__num = num
        self.__name = name
        self.__dye_type = DyeType.from_string(dye_type)

    @property
    def dye_type(self) -> DyeType:
        return self.__dye_type
    
    @property
    def name(self) -> str:
        return self.name

    def __eq__(self, other: Self) -> bool:
        return self.__dye_type == other.__dye_type
    
    def __lt__(self, other: Self) -> bool:
        return self.__dye_type < other.__dye_type
    
    def __str__(self) -> str:
        return f'COLOR[num={self.__num}, name=\'{self.__name}\', type=\'{self.__dye_type}]'
    
class Color(_ColorBase):
    pass