#!/usr/bin/env python

from typing import Protocol, Callable, TypeVar, ParamSpec, Concatenate, TypedDict
from abc import abstractmethod

T = TypeVar('T')
P = ParamSpec('P')

_CTR = 0

class FormattedArgs(TypedDict, total=False):
    desc1: str
    desc2: str
    desc3: str

class FormattedRet(TypedDict, total=False):
    result: str
    notes1: str
    notes2: str

class Process:

    def __init__(self, caller: int, name: str, desc1: str = 'N/A', desc2: str = 'N/A',
                 desc3: str = 'N/A'):
        globals()['_CTR'] += 1
        self.id: int = globals()['_CTR']
        self.caller = caller
        self.name = name
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3
        self.result = 'N/A'
        self.notes1 = 'N/A'
        self.notes2 = 'N/A'

    def set_result(self, result: str = 'N/A', notes1: str = 'N/A', notes2: str = 'N/A'):
        self.result = result
        self.notes1 = notes1
        self.notes2 = notes2

class Logger:

    def __init__(self):
        self.processes: list[Process] = []
        self.callers: list[int] = [0]
    
    def peek_caller(self) -> int:
        return self.callers[-1]

    def push_caller(self, process: Process) -> None:
        self.callers.append(process.id)
    
    def pop_caller(self) -> Process:
        return self.callers.pop()
    
    def add_process(self, proc: Process) -> None:
        self.processes.append(proc)

class LoggedType(Protocol):
    
    @property
    @abstractmethod
    def logger(self) -> Logger:
        raise NotImplementedError()
    
type LoggedMeth[**P, T] = Callable[Concatenate[LoggedType, P], T]

def logged_method(arg_fmtr: Callable[P, FormattedArgs],
                  ret_fmtr: Callable[[T], FormattedRet]) -> \
    Callable[[LoggedMeth[P, T]], LoggedMeth[P, T]]:
    def deco(f: LoggedMeth[P, T]) -> LoggedMeth[P, T]:
        def wrapper(slf: LoggedType, *args: P.args, **kwargs: P.kwargs) -> T:
            caller = slf.logger.peek_caller()
            p = Process(caller, f.__name__, **arg_fmtr(*args, **kwargs))
            slf.logger.add_process(p)
            slf.logger.push_caller(p)
            res = f(slf, *args, **kwargs)
            p.set_result(**ret_fmtr(res))
            slf.logger.pop_caller()
            return res
        return wrapper
    return deco

def logged_func(lgr: Logger, arg_fmtr: Callable[P, FormattedArgs],
                ret_fmtr: Callable[[T], FormattedRet]) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def deco(f: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            caller = lgr.peek_caller()
            p = Process(caller, f.__name__, **arg_fmtr(*args, **kwargs))
            lgr.add_process(p)
            lgr.push_caller(p)
            res = f(*args, **kwargs)
            p.set_result(**ret_fmtr(res))
            lgr.pop_caller()
            return res
        return wrapper
    return deco