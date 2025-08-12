from app.style.color.color import ShadeGrade as ShadeGrade, SOLUTION as SOLUTION, \
    LIGHT as LIGHT, MEDIUM as MEDIUM, BLACK as BLACK

from typing import Literal
from app.support import HasID, SuperImmut

type _RawShadeInt = Literal[1, 2, 3, 4]
type _RawShadeStr = Literal['LIGHT', 'MEDIUM', 'BLACK', 'SOLUTION']

class Color(HasID[str], SuperImmut):
    """
    A class for fabric color information. All properties are immutable.
    """

    name: str # The English name of the color
    shade: ShadeGrade # Either 0_SOLUTION, 1_LIGHT, 2_MEDIUM, or 3_BLACK

    def __init__(self, name: str, number: int, raw_shade: _RawShadeInt | _RawShadeStr) -> None:
        """
        Initialize a new Color object.

            name:
              The name of the color (as written in the Xref sheet).
            number:
              The dye formula as an integer. The 5-digit string will be used as the object's id.
            raw_shade:
              An integer 1-4 or a string indicating the "shade" of this color.
        """
        ...