from app.support import HasID, SuperImmut, FloatRange

class GreigeStyle(HasID[str], SuperImmut, attrs=('_prefix','id','roll_rng','port_rng'),
                  priv_attrs=('prefix','id'), frozen=('*prefix','*id','roll_rng','port_rng')):
    roll_rng: FloatRange # The standard weight range for rolls in this style
    port_rng: FloatRange # The standard port load for this style
    def __init__(self, id: str, port_min: float, port_max: float) -> None:
        """
        Initialize a new GreigeStyle object.

            id:
              The greige item number (as seen in the Demand Planning file).
            port_min:
              The minimum target pounds of this greige to load in a port.
            port_max:
              The maximum target pounds of this greige to load in a port.
        """
        ...

def init() -> None:
    """
    Initialize necessary components of app.style.greige sub-module. You must run this function
    before using this sub-module.
    """
    ...

def get_style(id: str) -> GreigeStyle | None:
    """
    Get a GreigeStyle object by its id. Although these are hashable and immutable, this prevents
    the creation of too many GreigeStyle objects, as well as allowing FabricStyle and Inventory
    data to be loaded without having all the necessary greige information.
    """
    ...