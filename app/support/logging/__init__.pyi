from typing import Protocol, Callable, TypeVar, ParamSpec, Concatenate, TypedDict, Generator
from abc import abstractmethod

_T = TypeVar('T')
_P = ParamSpec('P')

class FormattedArgs(TypedDict, total=False):
    desc1: str
    desc2: str
    desc3: str

class FormattedRet(TypedDict, total=False):
    result: str
    notes1: str
    notes2: str

class LogGenMsg:
    result: str
    notes1: str
    notes2: str
    def __init__(self, result: str = ..., notes1: str = ..., notes2: str = ...) -> None: ...
    def as_kwargs(self) -> FormattedRet: ...

class Process:
    id: int
    caller: int
    name: str
    desc1: str
    desc2: str
    desc3: str
    result: str
    notes1: str
    notes2: str
    def __init__(self, caller: int, name: str, desc1: str = ..., desc2: str = ...,
                 desc3: str = ...) -> None: ...
    def set_result(self, result: str = ..., notes1: str = ..., notes2: str = ...) -> None: ...

class Logger:
    processes: list[Process]
    callers: list[int]
    def __init__(self) -> None: ...
    def peek_caller(self) -> int: ...
    def push_caller(self, process: Process) -> None: ...
    def pop_caller(self) -> Process: ...
    def add_process(self, proc: Process) -> None: ...

class LoggedType(Protocol):
    @classmethod
    @abstractmethod
    def set_logger(cls, lgr: Logger) -> None: ...
    @property
    @abstractmethod
    def logger(self) -> Logger: ...
    
type LoggedMeth[**_P, _T] = Callable[Concatenate[LoggedType, _P], _T]
type LoggedGen[**_P, _T] = Callable[_P, Generator[_T | LogGenMsg]]
type ArgsFmtr[**_P] = Callable[_P, FormattedArgs]
type RetFmtr[_T] = Callable[[_T], FormattedRet]

def logged_method(arg_fmtr: ArgsFmtr[_P], ret_fmtr: RetFmtr[_T]) -> \
    Callable[[LoggedMeth[_P, _T]], LoggedMeth[_P, _T]]: ...

def logged_func(lgr: Logger, arg_fmtr: ArgsFmtr[_P], ret_fmtr: RetFmtr[_T]) -> \
    Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...

def logged_generator(lgr: Logger, arg_fmtr: ArgsFmtr[_P], yld_fmtr: RetFmtr[_T]) -> \
    Callable[[LoggedGen[_P, _T]], Callable[_P, Generator[_T]]]: ...