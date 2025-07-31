#!/usr/bin/env python

import os
import pandas as pd

from .style import Greige, translation
from .roll import Roll
from .inventory import Inventory

PREFIX = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling'
FNAME = 'master.xlsx'
SHEET = 'inventory'

def get_roll(df: pd.DataFrame, idx: int) -> Roll | None:
    inv_style = df.loc[idx, 'Item']
    greige_name = ''
    try:
        greige_name = translation.translate_style(inv_style)
    except ValueError:
        return None
    
    greige = Greige(greige_name)
    return Roll(df.loc[idx, 'Roll'], greige, df.loc[idx, 'Quantity'])

def load_inventory() -> Inventory:
    translation.init()
    
    inv = Inventory()
    df = pd.read_excel(os.path.join(PREFIX, FNAME),
                       sheet_name=SHEET,
                       usecols=['Plant', 'Roll', 'Item', 'Quality',
                                'UOM', 'Quantity', 'ASSIGNED_ORDER'],
                       dtype={
                           'Plant': 'string',
                           'Roll': 'string',
                           'Item': 'string',
                           'Quality': 'string',
                           'UOM': 'string',
                           'ASSIGNED_ORDER': 'string'
                       })
    sub_df = df[(df['Quality'] == 'A') & (df['UOM'] == 'LB') & df['ASSIGNED_ORDER'].isna()]

    for i in sub_df.index:
        newroll = get_roll(sub_df, i)
        if newroll is None: continue
        inv.add_roll(newroll)
    
    return inv