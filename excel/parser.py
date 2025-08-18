#!/usr/bin/env python

from typing import NamedTuple, Literal, Generator, Any
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

def get_lines(tok_stream: Generator[Token]) -> Generator[list[Token]]:
    cur_line: list[Token] = []
    at_start: bool = True
    while True:
        try:
            nxt = next(tok_stream)
            if at_start:
                if nxt.kind not in (TokenKind.COMMENT, TokenKind.NEWLINE):
                    cur_line.append(nxt)
            else:
                if nxt.kind not in (TokenKind.COMMENT, TokenKind.WS, TokenKind.NEWLINE):
                    cur_line.append(nxt)
            
            if nxt.kind == TokenKind.NEWLINE:
                yield cur_line
                cur_line = []
                at_start = True
            else:
                at_start = False
        except StopIteration:
            yield cur_line
            return
        
def is_context_name(line: list[Token]) -> bool:
    return len(line) == 2 and line[0].kind == TokenKind.NAME and line[1].kind == TokenKind.COLON

def split_contexts(tok_stream: Generator[Token]) -> dict[str, list[list[Token]]]:
    contexts: dict[str, list[list[Token]]] = {}
    cur_name: str = ''
    lines = get_lines(tok_stream)
    cur_line: list[Token] = []

    for line in lines:
        if not line: continue

        if cur_line:
            if line[-1].kind != TokenKind.ELLIPSIS:
                contexts[cur_name].append(cur_line + line[1:])
                cur_line = []
            else:
                cur_line += line[1:-1]
        elif is_context_name(line):
            cur_name = line[0].value
            contexts[cur_name] = []
        elif line[0].kind == TokenKind.WS and len(line[0].value) == 4:
            if line[-1].kind == TokenKind.ELLIPSIS:
                cur_line = line[1:-1]
            else:
                contexts[cur_name].append(line[1:])
    
    return contexts

def make_error_msg(name: str, values: list[Token]) -> str:
    token_str = ''.join([t.value for t in values])
    return f'Invalid value for \'{name}\': \'{token_str}\'.'

def parse_data_info(fpath: str) -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    f = open(fpath)
    tstream = make_token_stream(f)
    contexts = split_contexts(tstream)
    f.close()

    for ctxt, lines in contexts.items():
        parsed[ctxt] = {}

        for line in lines:
            line_str = ''.join([t.value for t in line])
            assert len(line) >= 3 and line[0].kind == TokenKind.NAME and line[1].kind == TokenKind.EQUALS, \
                f'All data info items must be in the form <name>=<value>.\nBad line: {line_str}'
            assert '.' not in line[0].value, f'Invalid name: {repr(line[0].value)}.'

            name, _, *values = line
            name = name.value
            values = list(filter(lambda t: t.kind != TokenKind.COMMA, values))

            match name:
                case 'excel_book' | 'sheet_name' | 'folder' | 'excel_columns':
                    if len(values) != 1 or values[0].kind not in (TokenKind.NAME, TokenKind.STRING):
                        raise SyntaxError(make_error_msg(name, values))
                    val = values[0].value
                    if values[0].kind == TokenKind.STRING:
                        val = val[1:-1]
                    parsed[ctxt][name] = val
                case 'start_row' | 'end_row':
                    if len(values) != 1 or values[0].kind != TokenKind.NUMBER:
                        raise SyntaxError(make_error_msg(name, values))
                    n = int(values[0].value)
                    parsed[ctxt][name] = n
                case 'columns' | 'column_names':
                    if not all(map(lambda t: t.kind in (TokenKind.NAME, TokenKind.STRING, TokenKind.NUMBER), values)):
                        raise SyntaxError(make_error_msg(name, values))
                    vals = []
                    for t in values:
                        if t.kind == TokenKind.STRING:
                            vals.append(t.value[1:-1])
                        else:
                            vals.append(t.value)
                    parsed[ctxt][name] = vals
                case _:
                    raise SyntaxError(f'Unrecognized keyword: \'{name}\'.')
    
    return parsed