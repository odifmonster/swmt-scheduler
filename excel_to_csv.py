#!/usr/bin/env python

from typing import Literal
import pandas as pd
import os, sys

import excel

type InfoKey = Literal['fabric_items', 'greige_sizes', 'greige_translation', 'jet_info']

APPDIR = os.path.join(os.path.dirname(__file__), 'app')

def run_trans_converts(df: pd.DataFrame) -> pd.DataFrame:
    df['inventory'] = df['inventory'].str.upper()
    df['plan'] = df['plan'].str.upper()
    sub_df = df[~df['plan'].str.contains(r'USED|DEV')]
    return sub_df

def run_fabric_converts(df: pd.DataFrame) -> pd.DataFrame:
    df['GREIGE ITEM'] = df['GREIGE ITEM'].str.upper()
    sub_df = df[~df['COLOR NUMBER'].isna() & ~df['Yield'].isna() & ~df['SHADE RATING'].isna() & ~df['PA FIN ITEM'].isna()]
    sub_df = sub_df[~sub_df['GREIGE ITEM'].str.contains('CAT')]
    return sub_df

def run_greige_converts(df: pd.DataFrame) -> pd.DataFrame:
    df['greige'] = df['greige'].str.upper()
    return df

def get_out_path(key: InfoKey) -> os.PathLike:
    match key:
        case 'fabric_items':
            return os.path.join(APPDIR, 'style', 'fabric', 'styles.csv')
        case 'greige_sizes':
            return os.path.join(APPDIR, 'style', 'greige', 'styles.csv')
        case 'greige_translation':
            return os.path.join(APPDIR, 'style', 'translate', 'translate.csv')
        case 'jet_info':
            return os.path.join(APPDIR, 'schedule', 'jet', 'jets.csv')

def get_row(key: InfoKey, df: pd.DataFrame, i: int) -> str:
    match key:
        case 'fabric_items':
            jets: list[str] = []
            for jeti in (1,2,3,4,7,8,9,10):
                if not pd.isna(df.loc[i, f'JET {jeti}']):
                    jets.append(f'Jet-{jeti:02}')
            row: list[str] = []
            row.append(df.loc[i, 'PA FIN ITEM'])
            row.append(df.loc[i, 'GREIGE ITEM'])
            row.append(df.loc[i, 'STYLE'])
            row.append(df.loc[i, 'COLOR NAME'])
            row.append(df.loc[i, 'COLOR NUMBER'])
            row.append(f'{df.loc[i, 'Yield']:.4f}')
            row.append(df.loc[i, 'SHADE RATING'])
            row.append(' '.join(jets))

            return ','.join([str(x) for x in row]) + '\n'
        case 'greige_sizes':
            grg = df.loc[i, 'greige']
            tgt_lbs = df.loc[i, 'tgt_lbs']
            return f'{grg},{tgt_lbs-20:.2f},{tgt_lbs+20:.2f}\n'
        case 'greige_translation':
            return f'{df.loc[i, 'inventory']},{df.loc[i, 'plan']}\n'
        case 'jet_info':
            return f'{df.loc[i, 'jet']},{df.loc[i, 'alt_jet']},{df.loc[i, 'n_ports']},' + \
                f'{df.loc[i, 'min_load']},{df.loc[i, 'max_load']}\n'

def write_csv(key: InfoKey) -> None:
    excel.init()

    outpath = get_out_path(key)
    outfile = open(outpath, mode='w+')

    inpath, pdargs = excel.get_excel_info(key)
    df = pd.read_excel(inpath, **pdargs)
    match key:
        case 'fabric_items':
            df = run_fabric_converts(df)
        case 'greige_translation':
            df = run_trans_converts(df)
        case 'greige_sizes':
            df = run_greige_converts(df)

    for i in df.index:
        outfile.write(get_row(key, df, i))
    
    outfile.close()

if __name__ == '__main__':
    write_csv(sys.argv[1])