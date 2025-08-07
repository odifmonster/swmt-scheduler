from typing import NewType, Literal

ShadeGrade = NewType('ShadeGrade', str)
SOLUTION = ShadeGrade('0_SOLUTION')
LIGHT = ShadeGrade('1_LIGHT')
MEDIUM = ShadeGrade('2_MEDIUM')
BLACK = ShadeGrade('3_BLACK')

type _RawShadeInt = Literal[1, 2, 3, 4]
type _RawShadeStr = Literal['LIGHT', 'MEDIUM', 'BLACK', 'SOLUTION']

class Color:
    """
    A class for storing information about fabric style colors.
    """
    def __init__(self, name: str, number: int, shade: _RawShadeInt | _RawShadeStr) -> None:
        """
        Initialize a new Color object.
        name: the English name of the color
        number: the dye formula number
        shade: an int (from 1 to 4) or a string representing the shade "grade"
        """
        ...
    @property
    def name(self) -> str: ...
    @property
    def number(self) -> str: ...
    @property
    def shade(self) -> ShadeGrade: ...
    def __repr__(self) -> str: ...