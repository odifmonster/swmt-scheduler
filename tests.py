#!/usr/bin/env python

from typing import TypedDict, Unpack
from app.support import SuperImmut

class CustomKwargs(TypedDict, total=False):
    kind: str
    name: str
    value: int

class CustomImmutable(SuperImmut,
                      attrs=['kind', 'name', 'value'],
                      defaults={'kind': 'Data'}):

    def __init__(self, **kwargs: Unpack[CustomKwargs]):
        super().__init__(**kwargs)
    
    def is_negative(self) -> bool:
        return self.value < 0

def main():
    test = CustomImmutable(name='Test', value=10)
    test2 = CustomImmutable(kind='NegData', name='Test2', value=-10)
    print(test.is_negative(), test2.is_negative())
    try:
        test.name = 'NewName'
    except AttributeError:
        print('Failed to set attribute! Yay!')
    
    try:
        test2.some_attr = []
    except AttributeError:
        print('Failed to set instance attribute! Yay!')

if __name__ == '__main__':
    main()