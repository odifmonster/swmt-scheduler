#!/usr/bin/env python

from typing import Protocol, Callable, Generator, Any
from abc import abstractmethod

_CTR = 0

class Process:

    def __init__(self, caller, name):
        globals()['_CTR'] += 1
        self.id = globals()['_CTR']
        self.caller = caller
        self.name = name
        self.desc1, self.desc2, self.desc3 = '', '', ''

    def set_desc(self, desc1 = '', desc2 = '', desc3 = ''):
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3

class Logger:
    
    def __init__(self):
        self.processes: list[Process] = []
        self.callers = [0]

    def _get_insert_idx(self, id: int, lo: int, hi: int):
        if hi <= lo:
            return lo
        
        mid = int((lo + hi) / 2)
        if id > self.processes[mid].id:
            return self._get_insert_idx(id, mid+1, hi)
        return self._get_insert_idx(id, lo, mid)

    def add_process(self, p: Process):
        idx = self._get_insert_idx(p.id, 0, len(self.processes))
        self.processes.insert(idx, p)
    
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

    def __init__(self, desc1 = '', desc2 = '', desc3 = ''):
        self.desc1 = desc1
        self.desc2 = desc2
        self.desc3 = desc3
    
    def as_dict(self):
        return {
            'desc1': self.desc1, 'desc2': self.desc2, 'desc3': self.desc3
        }

ProcessDesc = dict

def _log_func_call(lgr: Logger, desc_args, desc_ret, func, *args, **kwargs):
    callp = Process(lgr.peek_caller(), func.__name__)
    callp.set_desc(**desc_args(*args, **kwargs))
    lgr.add_process(callp)
    lgr.push_caller(callp)

    res = func(*args, **kwargs)
    lgr.pop_caller()
    retp = Process(callp.id, f'return({func.__name__})')
    retp.set_desc(**desc_ret(res))
    lgr.add_process(retp)

    return res

def logged_func(lgr: Logger, desc_args, desc_ret):
    def deco(func: Callable):
        def wrapper(*args, **kwargs):
            return _log_func_call(lgr, desc_args, desc_ret, func, *args, **kwargs)
        return wrapper
    return deco

def logged_meth(desc_args, desc_ret):
    def deco(func: Callable):
        def wrapper(slf: HasLogger, *args, **kwargs):
            return _log_func_call(slf.logger, desc_args, desc_ret, func, slf, *args, **kwargs)
        return wrapper
    return deco

def logged_generator(desc_args, desc_yld):
    def deco(func: Callable[[*tuple[Any, ...]], Generator[FailedYield | Any]]):
        def wrapper(slf: HasLogger, *args, **kwargs):
            genp = Process(slf.logger.peek_caller(), func.__name__)
            genp.set_desc(**desc_args(slf, *args, **kwargs))
            slf.logger.add_process(genp)
            gen = func(slf, *args, **kwargs)

            while True:
                nextp = Process(genp.caller, f'next({func.__name__})')
                slf.logger.push_caller(nextp)

                try:
                    val = next(gen)
                    slf.logger.add_process(nextp)
                    valp = Process(nextp.id, '')
                    slf.logger.add_process(valp)

                    if isinstance(val, FailedYield):
                        valp.name = 'yield_failure'
                        valp.set_desc(**(val.as_dict()))
                        slf.logger.pop_caller()
                        continue

                    valp.name = 'yield_value'
                    valp.set_desc(**desc_yld(val))
                    slf.logger.pop_caller()
                    yield val
                except StopIteration:
                    nextp.name = f'terminate({func.__name__})'
                    slf.logger.pop_caller()
                    return
        return wrapper
    return deco