#!/usr/bin/env python

from collections.abc import KeysView

from app.support import SuperIter
from app.support.groups import BaseGroup
from .temp import Data, DataView

class AKeysIter(SuperIter[DataView, str], get_val=lambda dv: dv.id):
    pass

class AKeysView(KeysView[str]):

    def __init__(self, link: BaseGroup[Data, DataView, str]):
        self.__link = link

    def __repr__(self):
        res = ''
        nxt_line = 'group_keys(['

        for i, item in enumerate(self.__link.iter_items()):
            nxt_str = item.pretty(kind='key')

            if len(nxt_line) > 0 and len(nxt_line) + len(nxt_str) > 73:
                if i > 0: nxt_line += ','
                if len(res) > 0: res += '\n'
                res += nxt_line
                nxt_line = nxt_str
            else:
                if i > 0:
                    nxt_line += ', '
                nxt_line += nxt_str
        
        nxt_line += '])'
        if len(res) > 0: res += '\n'
        res += nxt_line
        return res
    
    def __len__(self): return self.__link.n_items

    def __iter__(self): return AKeysIter(self.__link.iter_items())

    def __contains__(self, key: str): return key in self.__link