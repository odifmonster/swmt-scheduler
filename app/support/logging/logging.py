#!/usr/bin/env python

from typing import TypeVar, ParamSpec, Concatenate, Protocol, TypedDict, Callable, Generator
from abc import abstractmethod

T = TypeVar('T')
P = ParamSpec('P')

_CTR = 0

class Process:

    def __init__(self, caller: int, name: str, desc1: str = '', desc2: str = '',
                 desc3: str = ''):
        globals()['_CTR'] += 1
        self.id = globals()['_CTR']
        self.caller = caller
        self.name = name
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3

    def set_desc(self, desc1: str = '', desc2: str = '', desc3: str = ''):
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3

class Logger:
    
    def __init__(self):
        self.processes: list[Process] = []
        self.callers: list[int] = [0]

    def add_process(self, p: Process):
        self.processes.append(p)
    
    def push_caller(self, p: Process):
        self.callers.append(p.id)
    
    def pop_caller(self):
        return self.callers.pop()
    
    def peek_caller(self):
        return self.callers[-1]

class HasLogger(Protocol):

    @classmethod
    @abstractmethod
    def set_logger(cls, lgr: Logger):
        raise NotImplementedError()

    @property
    @abstractmethod
    def logger(self) -> Logger:
        raise NotImplementedError()

class FailedYield:

    def __init__(self, desc1: str = '', desc2: str = '', desc3: str = ''):
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3

class ProcessDesc(TypedDict, total=False):
    desc1: str
    desc2: str
    desc3: str

type DescArgsFunc[**P] = Callable[P, ProcessDesc]
type DescRetFunc[T] = Callable[[T], ProcessDesc]

def logged_func(lgr: Logger, desc_args: DescArgsFunc[P], desc_ret: DescRetFunc[T]) \
    -> Callable[[Callable[P, T]], Callable[P, T]]:
    def deco(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            callp = Process(lgr.peek_caller(), func.__name__, **desc_args(*args, **kwargs))
            lgr.add_process(callp)
            lgr.push_caller(callp)

            res = func(*args, **kwargs)
            lgr.pop_caller()
            retp = Process(callp.id, f'return({func.__name__})', **desc_ret(res))
            lgr.add_process(retp)

            return res
        return wrapper
    return deco

type LoggedMeth[**P, T] = Callable[Concatenate[HasLogger, P], T]

def logged_meth(desc_args: DescArgsFunc[P], desc_ret: DescRetFunc[T]) \
    -> Callable[[LoggedMeth[P, T]], LoggedMeth[P, T]]:
    def deco(func: LoggedMeth[P, T]) -> LoggedMeth[P, T]:
        def wrapper(slf: HasLogger, *args: P.args, **kwargs: P.kwargs) -> T:
            callp = Process(slf.logger.peek_caller(), func.__name__, **desc_args(*args, **kwargs))
            slf.logger.add_process(callp)
            slf.logger.push_caller(callp)

            res = func(slf, *args, **kwargs)
            slf.logger.pop_caller()
            retp = Process(callp.id, f'return({func.__name__})', **desc_ret(res))
            slf.logger.add_process(retp)

            return res
        return wrapper
    return deco

type LoggedGen[**P, T] = Callable[P, Generator[T]]

def logged_generator(lgr: Logger, desc_args: DescArgsFunc[P], desc_yld: DescRetFunc[T]) \
    -> Callable[[LoggedGen[P, T | FailedYield]], LoggedGen[P, T]]:
    def deco(func: LoggedGen[P, T | FailedYield]) -> LoggedGen[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Generator[T]:
            genp = Process(lgr.peek_caller(), func.__name__, **desc_args(*args, **kwargs))
            lgr.add_process(genp)
            gen = func(*args, **kwargs)
            while True:
                nextp = Process(genp.caller, f'next({func.__name__})')
                lgr.push_caller(nextp)

                try:
                    val = next(gen)
                    lgr.add_process(nextp)
                    valp = Process(nextp.id, '')
                    lgr.add_process(valp)

                    if isinstance(val, FailedYield):
                        valp.name = 'yield_failure'
                        valp.set_desc(val.desc1, val.desc2, val.desc3)
                        lgr.pop_caller()
                        continue

                    valp.name = f'yield({func.__name__})'
                    valp.set_desc(**desc_yld(val))
                    lgr.pop_caller()
                    yield val
                except StopIteration:
                    nextp.name = f'terminate({func.__name__})'
                    lgr.pop_caller()
                    return
        return wrapper
    return deco