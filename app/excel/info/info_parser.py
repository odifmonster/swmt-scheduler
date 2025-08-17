#!/usr/bin/env python

from typing import NamedTuple, Literal, Generator
from enum import Enum, auto
from io import TextIOBase

class TokenKind(Enum):
    COLON = auto()
    NEWLINE = auto()
    EQUALS = auto()
    COMMA = auto()
    ELLIPSIS = auto()
    WS = auto()
    COMMENT = auto()
    STRING = auto()
    NAME = auto()
    NUMBER = auto()

class Token(NamedTuple):
    kind: TokenKind
    value: str

class StreamPos(NamedTuple):
    line: int
    offset: int

class StreamWrapper:

    def __init__(self, f: TextIOBase):
        self.__f = f

    @property
    def pos(self) -> StreamPos:
        cur_pos = self.__f.tell()
        self.__f.seek(0)

        line, offset = 1, 0
        while self.__f.tell() < cur_pos:
            nxt = self.__f.read(1)
            if nxt == '\n':
                line += 1
                offset = 0
            else:
                offset += 1
            
        return StreamPos(line, offset)

    def read(self) -> str:
        return self.__f.read(1)
    
    def backup(self) -> None:
        pos = self.__f.tell()
        self.__f.seek(pos-1)

def is_alpha(c: str) -> bool:
    return (ord(c) >= ord('a') and ord(c) <= ord('z')) or \
        (ord(c) >= ord('A') and ord(c) <= ord('Z')) or \
        c == '_'

def is_num(c: str) -> bool:
    return ord(c) >= ord('0') and ord(c) <= ord('9')

def is_alpha_num(c: str) -> bool:
    return is_alpha(c) or is_num(c)

def next_dots(stream: StreamWrapper, prev: Literal['.']) -> str:
    res = prev
    for _ in range(2):
        nxt = stream.read()
        if len(nxt) == 0:
            raise SyntaxError(f'Unexpected EOF on line {stream.pos.line}.')
        if nxt != '.':
            raise SyntaxError(f'Unexpected character {repr(nxt)} on line {stream.pos.line}.')
        res += nxt
    return res

def next_spaces(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        return prev
    if nxt != ' ':
        stream.backup()
        return prev
    return next_spaces(stream, prev+nxt)

def next_comment(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        return prev
    if nxt == '\n':
        stream.backup()
        return prev
    return next_comment(stream, prev+nxt)

def next_string(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        raise SyntaxError(f'Unexpected EOF on line {stream.pos.line}.')
    if nxt == '\n':
        raise SyntaxError(f'Unclosed string on line {stream.pos.line}.')
    if nxt == '"':
        return prev+nxt
    return next_string(stream, prev+nxt)

def next_file_ext(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        raise SyntaxError(f'Unecpected EOF on line {stream.pos.line}.')
    if not is_alpha(nxt):
        raise SyntaxError(f'Unexpected character {repr(nxt)} on line {stream.pos.line}.')
    return next_name(stream, prev+nxt)

def next_name(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        return prev
    if is_alpha_num(nxt):
        return next_name(stream, prev+nxt)
    if nxt == '.':
        return next_file_ext(stream, prev+nxt)
    stream.backup()
    return prev

def next_number(stream: StreamWrapper, prev: str) -> str:
    nxt = stream.read()
    if len(nxt) == 0:
        return prev
    if is_num(nxt):
        return next_number(stream, prev+nxt)
    stream.backup()
    return prev

def make_token_stream(f: TextIOBase) -> Generator[Token]:
    stream = StreamWrapper(f)
    while True:
        nxt = stream.read()
        if len(nxt) == 0:
            return
        
        if nxt == ':':
            yield Token(TokenKind.COLON, nxt)
        elif nxt == '\n':
            yield Token(TokenKind.NEWLINE, nxt)
        elif nxt == '=':
            yield Token(TokenKind.EQUALS, nxt)
        elif nxt == ',':
            yield Token(TokenKind.COMMA, nxt)
        elif nxt == '.':
            res = next_dots(stream, nxt)
            yield Token(TokenKind.ELLIPSIS, res)
        elif nxt == ' ':
            res = next_spaces(stream, nxt)
            yield Token(TokenKind.WS, res)
        elif nxt == '#':
            res = next_comment(stream, nxt)
            yield Token(TokenKind.COMMENT, res)
        elif nxt == '"':
            res = next_string(stream, nxt)
            yield Token(TokenKind.STRING, res)
        elif is_alpha(nxt):
            res = next_name(stream, nxt)
            yield Token(TokenKind.NAME, res)
        elif is_num(nxt):
            res = next_number(stream, nxt)
            yield Token(TokenKind.NUMBER, res)
        else:
            raise SyntaxError(f'Unrecognized character {repr(nxt)} on line {stream.pos.line}.')