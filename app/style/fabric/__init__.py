#!/usr/bin/env python

from . import color
from .color import Color
from .fabric import FabricStyle
from .styles import init, get_style

__all__ = ['color', 'Color', 'FabricStyle', 'init', 'get_style']