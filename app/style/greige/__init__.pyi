from app.support import HasID, SuperImmut, FloatRange

class GreigeStyle(HasID[str], SuperImmut):
    """
    A class for greige style information. All properties are immutable.
    """

    port_range: FloatRange # The range of pounds allowed in one port
    roll_range: FloatRange # The range of pounds standard to a roll

    def __init__(self, item: str, port_min: float, port_max: float) -> None:
        """
        Initialize a new GreigeStyle object.

            item:
              The style's (translated) item number. Becomes the object's id.
            port_min:
              The minimum number of pounds to load on one port.
            port_max:
              The maximum number of pounds to load on one port.
        """
        ...

def init() -> None:
    """
    Initialize necessary components of app.style.greige sub-module. You must run this
    function before using this sub-module.
    """
    ...

def get_greige_style(id: str) -> GreigeStyle | None:
    """
    Returns the GreigeStyle object with the given id, or None if it does not exist.
    """
    ...