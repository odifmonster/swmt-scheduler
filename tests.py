#!/usr/bin/env python

from app import helper

@helper.decors.setterlike
def fib(n: int) -> int:
    if n < 2: return n
    return fib(n-2) + fib(n-1)

if __name__ == '__main__':
    print(fib(5))
    print(getattr(fib, '_setterlike'))