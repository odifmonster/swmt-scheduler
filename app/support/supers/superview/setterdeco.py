#!/usr/bin/env python

def setter_like(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(wrapper, '_setter_like', 1)
    return wrapper