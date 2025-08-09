#!/usr/bin/env python

import pandas as pd
import os

FPATH = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling/master.xlsx'
XREF_SHEET = 'Xref'
OUTFILE = 'styles.csv'

def load_xref_df():
    jet_cols = [f'JET {i}' for i in (1, 2, 3, 4, 7, 8, 9, 10)]
    usecols = ['GREIGE ITEM', 'Yield', 'STYLE', 'COLOR NAME', 'COLOR NUMBER', 'PA FIN ITEM'] \
        + jet_cols + ['SHADE RATING']
    dtype = {}
    for col in usecols:
        if col not in ('Yield', 'COLOR NUMBER', 'SHADE RATING'):
            dtype[col] = 'string'
    
    df = pd.read_excel(FPATH, sheet_name=XREF_SHEET, usecols=usecols, dtype=dtype)
    df['GREIGE ITEM'] = df['GREIGE ITEM'].str.upper()
    sub_df = df[~(df['SHADE RATING'].isna() | df['PA FIN ITEM'].isna())]
    return sub_df

def write_xref_df(df: pd.DataFrame):
    outfile = open(os.path.join(os.path.dirname('__file__'), OUTFILE), 'w+')

    for i in df.index:
        item = df.loc[i, 'PA FIN ITEM']
        greige = df.loc[i, 'GREIGE ITEM']
        yld = df.loc[i, 'Yield']
        master = df.loc[i, 'STYLE']
        clr_name = df.loc[i, 'COLOR NAME']
        clr_num = df.loc[i, 'COLOR NUMBER']
        shade = df.loc[i, 'SHADE RATING']
        jets = []
        for i in (1, 2, 3, 4, 7, 8, 9, 10):
            if not pd.isnull(df.loc[i, f'JET {i}']):
                jets.append(f'Jet-{i:02}')
        
        jet_str = ' '.join(jets)
        outfile.write(f'{item},{greige},{yld:.6f},{master},{clr_name},{clr_num:0.0f},{shade:0.0f},{jet_str}\n')
    
    outfile.close()

if __name__ == '__main__':
    write_xref_df(load_xref_df())