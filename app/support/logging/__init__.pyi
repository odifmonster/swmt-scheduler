from typing import Protocol, TypedDict, TypeVar, ParamSpec, Concatenate, Callable, Generator
from abc import abstractmethod

_T = TypeVar('_T')
_P = ParamSpec('_P')

class Process:
    id: int
    caller: int
    name: str
    desc1: str
    desc2: str
    desc3: str
    def __init__(self, caller: int, name: str, desc1: str = '', desc2: str = '',
                 desc3: str = '') -> None: ...

class Logger:
    processes: list[Process]
    def __init__(self) -> None: ...
    def add_process(self, p: Process) -> None: ...
    def push_caller(self, p: Process) -> None: ...
    def pop_caller(self) -> int: ...
    def peek_caller(self) -> int: ...

class HasLogger(Protocol):
    @classmethod
    @abstractmethod
    def set_logger(cls, lgr: Logger) -> None: ...
    @property
    @abstractmethod
    def logger(self) -> Logger: ...

class FailedYield:
    desc1: str
    desc2: str
    desc3: str
    def __init__(self, desc1: str = '', desc2: str = '', desc3: str = '') -> None: ...

class ProcessDesc(TypedDict, total=False):
    desc1: str
    desc2: str
    desc3: str

type DescArgsFunc[**P] = Callable[P, ProcessDesc]
type DescRetFunc[T] = Callable[[T], ProcessDesc]

def logged_func(lgr: Logger, desc_args: DescArgsFunc[_P], desc_ret: DescRetFunc[_T]) \
    -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...

type LoggedMeth[**P, T] = Callable[Concatenate[HasLogger, P], T]

def logged_meth(desc_args: DescArgsFunc[_P], desc_ret: DescRetFunc[_T]) \
    -> Callable[[LoggedMeth[_P, _T]], LoggedMeth[_P, _T]]: ...

type LoggedGen[**P, T] = Callable[P, Generator[T]]

def logged_generator(lgr: Logger, desc_args: DescArgsFunc[_P], desc_yld: DescRetFunc[_T]) \
    -> Callable[[LoggedGen[_P, _T | FailedYield]], LoggedGen[_P, _T]]: ...