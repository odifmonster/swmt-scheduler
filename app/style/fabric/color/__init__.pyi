from app.style.fabric.color.color import ShadeGrade as ShadeGrade, HEAVYSTRIP as HEAVYSTRIP, \
    STRIP as STRIP, EMPTY as EMPTY, SOLUTION as SOLUTION, LIGHT as LIGHT, \
    MEDIUM as MEDIUM, BLACK as BLACK

from typing import Literal
import datetime as dt
from app.support import HasID, SuperImmut

type _RawShadeName = Literal['HEAVYSTRIP', 'STRIP', 'EMPTY', 'SOLTUION', 'LIGHT',
                             'MEDIUM', 'BLACK']
type _RawShadeInt = Literal[1, 2, 3, 4, 5, 6, 7]
type _RawShadeVal = _RawShadeName | _RawShadeInt

class Color(HasID[str], SuperImmut,
            attrs=('_prefix','id','name','number','shade','soil','cycle_time'),
            frozen=('name','number','shade','soil','cycle_time')):
    """
    A class for Color objects. All attributes are immutable.
    """
    name: str
    number: int
    shade: ShadeGrade
    soil: int # the "soil level" this color will add to a jet
    cycle_time: dt.timedelta
    def __init__(self, name: str, number: int, shade_val: _RawShadeVal) -> None:
        """
        Initialize a new Color object.

            name:
              The English name of the color.
            number:
              The dye formula (as an integer).
            shade_val:
              A string or integer 1-7 indicating the shade of this color.
              5-7 represent EMPTY, STRIP, and HEAVYSTRIP.
        """
        ...