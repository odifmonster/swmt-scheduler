#!/usr/bin/env python

from typing import TypeVar, Protocol, Generic

from .has_id import HasID
from .viewable import Viewable
from .pretty import SupportsPretty, PrettyArgsOpt

_T = TypeVar('_T', str, int)
_U_co = TypeVar('_U_co', bound=PrettyArgsOpt, covariant=True)

class SupportsPrettyID(Generic[_T, _U_co], SupportsPretty[_U_co], HasID[_T], Protocol):
    pass

__all__ = ['HasID', 'Viewable', 'SupportsPretty', 'SupportsPrettyID',
           'PrettyArgsOpt']