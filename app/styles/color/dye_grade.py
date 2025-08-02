#!/usr/bin/env python

from typing import Self

class DyeGrade:

    def __init__(self, val):
        str_to_dg = {
            'LIGHT': '1_LIGHT', 'MEDIUM': '2_MEDIUM',
            'BLACK': '3_BLACK', 'SOLUTION': '0_SOLUTION'
        }
        int_to_dg = ['1_LIGHT', '2_MEDIUM',
                     '3_BLACK', '0_SOLUTION']
        
        if type(val) is str:
            try:
                self.__grade = str_to_dg[val]
            except KeyError:
                raise TypeError(f'Unknown dye grade \'{val}\'.')
        elif type(val) is int:
            if val < 1 or val > 4:
                raise TypeError(f'Unknown dye grade {val}.')
            self.__grade = int_to_dg[val-1]
        else:
            raise TypeError(f'Cannot initialize dye grade with type {type(val)}.')
    
    def __str__(self):
        return self.__grade
    
    def __eq__(self, value: Self):
        return self.__grade == value.__grade
    
    def __lt__(self, value: Self):
        return self.__grade < value.__grade