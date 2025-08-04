#!/usr/bin/env python

from typing import Any

from app.support import Viewable
from app.support.groups import Item
from .mapped_like import MappedLike, MappedView
from .mapped_iter import MappedIter, MIDIter
from ..temp import Data, DPrettyArgsOpt

INITSIZE = 256
SKIP_LEN = 7
MAX_SATUR = 0.8

class Mapped(MappedLike, Viewable[MappedView]):

    def __init__(self, initize: int = INITSIZE, subattrs: tuple = (), **kwargs):
        self.__contents = [Item[str, DPrettyArgsOpt]() for _ in range(initize)]
        self.__size = initize
        self.__length = 0
        self.__insert_idx = 0

        self.__match_attrs = kwargs
        self.__sub_attrs = subattrs
        self.__groups: dict[Any, Mapped] = {}

        self.__view = MappedView(self)

    @property
    def n_items(self): return self.__length

    def _get_nearest_idx(self, id: str, skip_inserted: bool):
        idx = hash(id) % self.__size
        n_skips = 0

        while n_skips < self.__size:
            cur = self.__contents[idx]

            if not cur.inserted() or (not skip_inserted and cur.is_empty()) \
                or (not cur.is_empty() and cur.data.id == id):
                return idx
            
            idx = (idx + SKIP_LEN) % self.__size
            n_skips += 1
        
        return -1
    
    def _resize(self, newsize: int):
        pcontents = self.__contents

        self.__contents = [Item[str, DPrettyArgsOpt]() for _ in range(newsize)]
        self.__size = newsize

        for x in pcontents:
            if x.is_empty(): continue

            idx = self._get_nearest_idx(x.data.id, False)
            if idx < 0:
                raise ValueError(f'Cannot resize to size {newsize}.')
            
            self.__contents[idx] = x
    
    def _get_by_id(self, id: str):
        idx = self._get_nearest_idx(id, True)
        if idx >= 0:
            return self.__contents[idx]
        return None
    
    def _repr_props(self) -> str:
        contents = [f'  {prop}={repr(val)}' for prop, val in self.__match_attrs.items()]
        return '\n'.join(contents)
    
    def _match_props(self, data: Data) -> bool:
        for prop, val in self.__match_attrs.items():
            if getattr(data, prop) != val:
                return False
        return True
    
    def __len__(self):
        if len(self.__sub_attrs) == 0:
            return self.__length
        return len(self.__groups)

    def __iter__(self):
        if len(self.__sub_attrs) == 0:
            return MIDIter(MappedIter(self.__contents))
        return iter(self.__groups)
    
    def __contains__(self, key):
        if len(self.__sub_attrs) == 0:
            if type(key) not in (str, int):
                raise TypeError(f'Cannot check whether type {type(self)} contains key of type {type(key)}.')
            
            item = self._get_by_id(key)
            return not item is None and not item.is_empty()
        return key in self.__groups
    
    def __getitem__(self, key):
        if len(self.__sub_attrs) == 0:
            if type(key) is tuple:
                if len(key) > 1:
                    raise KeyError('Object does not accept multi-indexing.')
                key = key[0]
            
            item = self._get_by_id(key)
            if item is None or item.is_empty():
                raise KeyError(f'Object does not contain data with id {repr(key)}')
            return item.data
        elif not type(key) is tuple:
            return self.__groups[key].view()
        else:
            if len(key) == 1:
                return self.__groups[key[0]].view()
            return self.__groups[key[0]][key[1:]]
    
    def add(self, data: Data):
        item = self._get_by_id(data.id)
        if not item is None and not item.is_empty():
            return
        
        if not self._match_props(data):
            raise ValueError('Data added to this object must have the following properties:\n' \
                             + self._repr_props())
        
        if (self.__length + 1) / self.__size >= MAX_SATUR:
            self._resize(self.__size * 2)

        idx = self._get_nearest_idx(data.id, False)
        self.__insert_idx += 1
        self.__length += 1
        self.__contents[idx].store(data, self.__insert_idx-1)

        if len(self.__sub_attrs) > 0:
            val = getattr(data, self.__sub_attrs[0])
            if val not in self.__groups:
                subprops = { k: v for k, v in self.__match_attrs.items() }
                subprops[self.__sub_attrs[0]] = val
                self.__groups[val] = Mapped(subattrs=self.__sub_attrs[1:], **subprops)
            self.__groups[val].add(data)
    
    def remove(self, id: str):
        item = self._get_by_id(id)
        if item is None or item.is_empty():
            raise ValueError(f'Object does not contain data with id {repr(id)}.')
        
        self.__length -= 1
        data = item.clear()
        subgroup = self.__groups[getattr(data, self.__sub_attrs[0])]
        subgroup.remove(data.view().id)
        return data
    
    def view(self): return self.__view