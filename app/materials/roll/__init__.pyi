from app.materials.roll.roll import SizeClass as SizeClass, LARGE as LARGE, NORMAL as NORMAL, \
    SMALL as SMALL, HALF as HALF, PARTIAL as PARTIAL

import datetime as dt
from app.support import HasID, SuperImmut
from app.support.logging import HasLogger
from app.support.grouped import Data, DataView
from app.style import GreigeStyle
from app.materials.inventory import Snapshot

class RollAlloc(HasID[int], SuperImmut,
                attrs=('_prefix','id','roll_id','lbs','avail_date'),
                priv_attrs=('id',), frozen=('*id','roll_id','lbs','avail_date')):
    """Simple class for representing an allocation of a piece of one roll."""
    roll_id: str
    lbs: float
    avail_date: dt.datetime
    def __init__(self, roll_id: str, lbs: float, avail_date: dt.datetime) -> None: ...

class Roll(HasLogger, Data[str],
           mod_in_group=False,
           attrs=('_logger','logger','item','size','lbs','avail_date','snapshot'),
           priv_attrs=('init_wt','cur_wt','allocs','temp_allocs'),
           frozen=('*init_wt','item','avail_date')):
    """
    A class for Roll objects.
    """
    item: GreigeStyle
    avail_date: dt.datetime
    snapshot: Snapshot | None # The currently active inventory "snapshot"
    def __init__(self, id: str, item: GreigeStyle, lbs: float,
                 avail_date: dt.datetime) -> None:
        """
        Initialize a new Roll object.

            id:
              The id of this roll in inventory.
            item:
              The greige style of this roll.
            lbs:
              The weight of this roll.
        """
        ...
    @property
    def lbs(self) -> float:
        """The current weight of this roll."""
        ...
    @property
    def size(self) -> SizeClass:
        """The size of this roll relative to the standard for this item."""
        ...
    def allocate(self, lbs: float, snapshot: Snapshot | None = None) -> RollAlloc:
        """
        Allocate a piece of this roll.

            lbs:
              The number of pounds to allocate.
            snapshot: (default None)
              The Snapshot object (if any) to link the allocation to.
              If this is provided, the allocation is treated as a temporary
              usage applied within one inventory "snapshot". If this snapshot
              is not active, the roll will behave as though any linked
              allocations did not occur.
        
        Returns the RollAlloc object representing the used portion.
        """
        ...
    def deallocate(self, piece: RollAlloc, snapshot: Snapshot | None = None) -> None:
        """
        Deallocate a piece of this roll. Must be an object returned by this Roll's
        'allocate' method. Provide a snapshot if the allocation was temporary.
        """
        ...
    def apply_snap(self, snapshot: Snapshot | None = None) -> None:
        """
        Applies the given snapshot (if any) permanently). Removes all stored
        snapshots for garbage collection.
        """
        ...
    def view(self) -> RollView: ...

class RollView(DataView[str], attrs=('item','size','lbs','avail_date','snapshot'),
               funcs=('allocate','deallocate','release_snaps'),
               dunders=('repr',)):
    item: GreigeStyle
    avail_date: dt.datetime
    snapshot: Snapshot | None # The currently active inventory "snapshot"
    def __init__(self, link: Roll) -> None: ...
    @property
    def lbs(self) -> float:
        """The current weight of this roll."""
        ...
    @property
    def size(self) -> SizeClass:
        """The size of this roll relative to the standard for this item."""
        ...
    def allocate(self, lbs: float, snapshot: Snapshot | None = None) -> RollAlloc:
        """
        Allocate a piece of this roll.

            lbs:
              The number of pounds to allocate.
            snapshot: (default None)
              The Snapshot object (if any) to link the allocation to.
              If this is provided, the allocation is treated as a temporary
              usage applied within one inventory "snapshot". If this snapshot
              is not active, the roll will behave as though any linked
              allocations did not occur.
        
        Returns the RollAlloc object representing the used portion.
        """
        ...
    def deallocate(self, piece: RollAlloc, snapshot: Snapshot | None = None) -> None:
        """
        Deallocate a piece of this roll. Must be an object returned by this Roll's
        'allocate' method. Provide a snapshot if the allocation was temporary.
        """
        ...
    def apply_snap(self, snapshot: Snapshot | None = None) -> None:
        """
        Applies the given snapshot (if any) permanently). Removes all stored
        snapshots for garbage collection.
        """
        ...