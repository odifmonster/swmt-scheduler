#!/usr/bin/env python

from typing import Protocol, TypedDict, Self
from abc import abstractmethod

class PrettyArgsOpt(TypedDict, total=False):
    maxlen: int
    maxlines: int

    @classmethod
    def validate(cls, val: Self) -> Self:
        if 'maxlen' in val and val['maxlen'] < 10:
            raise ValueError('Cannot specify \'maxlen\' less than 10.')
        if 'maxlines' in val and val['maxlines'] < 1:
            raise ValueError('Cannot specify \'maxlines\' less than 1.')
        return val

class SupportsPretty(Protocol):

    def shorten_line(self, line, **kwargs):
        if len(line) <= kwargs['maxlen']:
            return line
        end1 = len(line) - kwargs['maxlen'] - 8
        return line[:end1] + '...' + line[-3:]
    
    def shorten_lines(self, lines: list[str], **kwargs):
        if len(lines) <= kwargs['maxlines']:
            return lines
        if kwargs['maxlines'] == 1:
            return [self.shorten_line(lines[0] + lines[-1], **kwargs)]
        end1 = len(lines) - kwargs['maxlines'] - 3
        return lines[:end1] + ['...'] + lines[-2:]

    @abstractmethod
    def pretty(self, **kwargs): raise NotImplementedError()