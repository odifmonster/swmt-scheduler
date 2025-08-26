#!/usr/bin/env python

from app.materials import Inventory, Snapshot, RollAlloc

def add_back_piece(inv: Inventory, piece: RollAlloc, snapshot: Snapshot) -> None:
    roll = inv.remove(inv.get(piece.roll_id))
    roll.deallocate(piece, snapshot=snapshot)
    inv.add(roll)

def apply_snapshot(inv: Inventory, snap: Snapshot | None) -> None:
    views = list(inv.itervalues())
    for rview in views:
        roll = inv.remove(rview)
        roll.apply_snap(snap)
        inv.add(roll)