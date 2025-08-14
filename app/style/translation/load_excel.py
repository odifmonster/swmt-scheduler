#!/usr/bin/env python

import pandas as pd
import os

EXCEL_DIR = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling'
MASTER_FILE = 'master.xlsx'
TRANS_SHEET = 'greige_translation'
OUTFILE = 'translate.csv'

def load_trans_df():
    df = pd.read_excel(os.path.join(EXCEL_DIR, MASTER_FILE), sheet_name=TRANS_SHEET,
                       usecols=['inv_name', 'plan_name'], dtype='string')
    df['inv_name'] = df['inv_name'].str.upper()
    df['plan_name'] = df['plan_name'].str.upper()
    sub_df = df[~df['plan_name'].str.contains(r'USED|DEV')]
    return sub_df

def write_trans_df(df: pd.DataFrame):
    outfile = open(os.path.join(os.path.dirname(__file__), OUTFILE), 'w+')

    for i in df.index:
        inv = df.loc[i, 'inv_name']
        plan = df.loc[i, 'plan_name']
        outfile.write(','.join([inv, plan]) + '\n')
    
    outfile.close()

if __name__ == '__main__':
    write_trans_df(load_trans_df())