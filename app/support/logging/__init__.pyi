from typing import Protocol, TypedDict, Callable, Concatenate, Generator
from abc import abstractmethod

class Process:
    id: int
    caller: int
    name: str
    desc1: str
    desc2: str
    desc3: str
    def __init__(self, caller: int, name: str) -> None: ...
    def set_desc(self, desc1: str = '', desc2: str = '', desc3: str = '') -> None: ...

class Logger:
    processes: list[Process]
    callers: list[int]
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
    def as_dict(self) -> ProcessDesc: ...

class ProcessDesc(TypedDict, total=False):
    desc1: str
    desc2: str
    desc3: str

def logged_func[**P, T](
        lgr: Logger,
        desc_args: Callable[P, ProcessDesc],
        desc_ret: Callable[[T], ProcessDesc]) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

def logged_meth[**P, C: HasLogger, T](
        desc_args: Callable[Concatenate[C, P], ProcessDesc],
        desc_ret: Callable[[T], ProcessDesc]) \
            -> Callable[[Callable[Concatenate[C, P], T]], Callable[Concatenate[C, P], T]]: ...

type GenMethod[**P, C: HasLogger, T] = Callable[Concatenate[C, P], Generator[T]]

def logged_generator[**P, C: HasLogger, T](
        desc_args: Callable[Concatenate[C, P], ProcessDesc],
        desc_yld: Callable[[T], ProcessDesc]) \
            -> Callable[[GenMethod[P, C, FailedYield | T]], GenMethod[P, C, T]]: ...