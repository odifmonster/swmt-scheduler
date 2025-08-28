#!/usr/bin/env python

def setter_like(func):
    def wrapper(slf, *args, **kwargs):
        if hasattr(slf, '_in_group') and hasattr(type(slf), '_mod_in_group') \
            and not type(slf)._mod_in_group and slf._in_group:
            raise RuntimeError(f'\'{type(slf).__name__}\' objects cannot be mutated while in a group')
        return func(slf, *args, **kwargs)
    setattr(wrapper, '_setter_like', 1)
    return wrapper