from app.support import HasID, SuperImmut

class Snapshot(HasID[int], SuperImmut, attrs=('_prefix','id'), priv_attrs=('id',),
               frozen=('*id',)):
    """
    A class for uniquely identifying snapshots of inventory positions.
    Allows you to compare many different versions of the inventory
    without copying it over each time.
    """
    def __init__(self) -> None:
        """Initialize a new Snapshot object."""
        ...