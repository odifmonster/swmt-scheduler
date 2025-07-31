#!/usr/bin/env python

import pandas as pd
import os

PREFIX = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling'
XL_FILE = 'master.xlsx'
SHEET = 'translation_ana'

def write_trans_file(srcpath: str, sheet: str) -> None:
    df = pd.read_excel(srcpath,
                       sheet_name=sheet,
                       usecols=['inv_name','plan_name'],
                       dtype='string')
    df['inv_name'] = df['inv_name'].str.upper()
    df['plan_name'] = df['plan_name'].str.upper()

    used = df[~df['plan_name'].str.contains(r'USED|DEV')]

    outfile = open(os.path.join(os.path.dirname(__file__), 'trans.csv'), 'w+')
    for i in used.index:
        inv = used.loc[i, 'inv_name'].strip()
        plan = used.loc[i, 'plan_name'].strip()
        outfile.write(f'{inv},{plan}\n')
    
    outfile.close()

def main() -> None:
    write_trans_file(os.path.join(PREFIX, XL_FILE), SHEET)

if __name__ == '__main__':
    main()