#!/usr/bin/env python

from .data import Data

def match_props(data: Data, props: dict[str]) -> bool:
    for attr, val in props.items():
        if not getattr(data, attr) == val:
            return False
    return True

def repr_props(props: dict[str], indent: str = '  ') -> str:
    return '\n'.join(map(lambda x: indent + f'{x[0]}={repr(x[1])}', props.items()))