#!/usr/bin/env python

import pandas as pd
import os

EXCEL_DIR = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling'
MASTER_FILE = 'master.xlsx'
INFO_SHEET = 'greige_info'
OUTFILE = 'styles.csv'

def load_info_df():
    df = pd.read_excel(os.path.join(EXCEL_DIR, MASTER_FILE), sheet_name=INFO_SHEET,
                       dtype={'item': 'string', 'target_lbs': 'float64'})
    return df

def write_info_df(info_df: pd.DataFrame):
    outfile = open(os.path.join(os.path.dirname(__file__), OUTFILE), 'w+')
    for i in info_df.index:
        name = info_df.loc[i, 'item']
        lbs = info_df.loc[i, 'target_lbs']
        outfile.write(f'{name},{lbs:.1f}\n')
    outfile.close()

if __name__ == '__main__':
    write_info_df(load_info_df())