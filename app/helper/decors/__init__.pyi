from typing import TypeVar, ParamSpec, Callable

_T = TypeVar('_T')
_P = ParamSpec('_P')

def setterlike(f: Callable[_P, _T]) -> Callable[_P, _T]: ...