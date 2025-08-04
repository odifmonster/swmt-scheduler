#!/usr/bin/env python

from typing import Protocol, Iterator, Unpack

from app.support import SuperView, SupportsPretty, PrettyArgsOpt
from ..temp import Data

class MPrettyArgsOpt(PrettyArgsOpt, total=False):
    lpad: str

class MPrettyArgs(MPrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 60, maxlines = 8, lpad = ''):
        return cls(maxlen=maxlen, maxlines=maxlines, lpad=lpad)

class MappedLike(SupportsPretty[MPrettyArgsOpt], Protocol):

    @property
    def n_items(self) -> int: raise NotImplementedError()

    def __len__(self) -> int: raise NotImplementedError()

    def __iter__(self) -> Iterator[str]: raise NotImplementedError()

    def __contains__(self, key: str) -> bool: raise NotImplementedError()

    def add(self, data: Data) -> None: raise NotImplementedError()

    def remove(self, id: str) -> Data: raise NotImplementedError()

    def pretty(self, **kwargs: Unpack[MPrettyArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = MPrettyArgs.create(**opts)

        lines: list[str] = []
        cur_line: str = 'Mapped({'
        prefix: str = ' ' * len(cur_line)

        for key in self:
            if not lines and len(cur_line) == len(prefix):
                cur_line += repr(key)
            else:
                plen = 0 if len(lines) == 0 else len(prefix)
                cur_item = repr(key)
                
                if len(cur_line)+len(cur_item)+plen+2 >= opts['maxlen']:
                    cur_line += ','
                    lines.append(cur_line)
                    cur_line = cur_item
                else:
                    cur_line += ', '
                    cur_line += cur_item
        
        cur_line += '})'
        lines.append(cur_line)

        if opts['maxlines'] == 1:
            return self.shorten_line(' '.join(lines), **opts)
        
        lines = map(lambda x: x[1] if x[0] == 0 else prefix+x[1], enumerate(lines))
        lines = map(lambda x: self.shorten_line(x, **opts), lines)
        return '\n'.join(lines)

class MappedView(MappedLike,
                 SuperView[MappedLike],
                 no_access=['add', 'remove']):
    pass