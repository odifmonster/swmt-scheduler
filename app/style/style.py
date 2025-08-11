#!/usr/bin/env python

from .greige import init_greige
from .fabric import init_fabric

def init():
    init_greige()
    init_fabric()