#!/usr/bin/env python

from typing import TypeVar, Protocol, Generic

from .has_id import HasID
from .viewable import Viewable
from .pretty import SupportsPretty

_T = TypeVar('_T', str, int)

class SupportsPrettyID(Generic[_T], SupportsPretty, HasID[_T], Protocol):
    pass

__all__ = ['HasID', 'Viewable', 'SupportsPretty', 'SupportsPrettyID']