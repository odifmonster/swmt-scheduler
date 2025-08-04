#!/usr/bin/env python

from typing import Protocol

from app.support import SuperView
from ..temp import Data

class MappedLike(Protocol):

    @property
    def n_items(self) -> int: raise NotImplementedError()

    def add(self, data: Data) -> None: raise NotImplementedError()

    def remove(self, id: str) -> Data: raise NotImplementedError()

class MappedView(MappedLike,
                 SuperView[MappedLike],
                 no_access=['add', 'remove']):
    pass