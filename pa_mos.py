#!/usr/bin/env python

from typing import TypedDict
import sys, os, pandas as pd, datetime as dt
from loaddata import load_demand

class MOLinkTable(TypedDict):
    mo: list[str]
    process: list[str]
    yds_expected: list[float]
    item: list[str]
    ordered_yds: list[float]
    pnum: list[int]
    due_date: list[dt.datetime]

def load_1427_report(fpath: str):
    df = pd.read_excel(fpath, sheet_name='1427', skiprows=3,
                       usecols=['Warehouse', 'Customer', 'Roll', 'Lot',
                                'Item', 'Quality', 'Nominal\nWidth', 'Quantity',
                                'WEEKOF'],
                       dtype={
                           'Warehouse': 'string', 'Customer': 'string',
                           'Roll': 'string', 'Lot': 'string', 'Item': 'string',
                           'Quality': 'string'
                       })
    def convert_wd(wd: float):
        if pd.isna(wd):
            return 'NA'
        if int(wd) == wd:
            return str(int(wd))
        return str(wd)
    df['Item-Width'] = df['Item'] + '-' + \
        df['Nominal\nWidth'].apply(convert_wd).astype('string')
    return df[(df['Customer'] == '0171910WIP') & (df['Quality'] == 'A')]

def get_fin_and_mos(df: pd.DataFrame):
    insp_df = df[df['Warehouse'] == 'BG']
    insp_mos: dict[str, list] = {}
    for i in insp_df.index:
        item = insp_df.loc[i, 'Item-Width']
        if item not in insp_mos:
            insp_mos[item] = []
        
        mo_num = insp_df.loc[i, 'Lot']
        mo_qty = insp_df.loc[i, 'Quantity'] * 0.9
        week = dt.date.fromisoformat(insp_df.loc[i, 'WEEKOF'])
        insp_mos[item].append((mo_num, mo_qty, week))
    
    for item in insp_mos:
        insp_mos[item] = sorted(insp_mos[item], key=lambda x: x[2])
    
    frame_df = df[(df['Warehouse'] == 'BS') | (df['Warehouse'] == 'BF')]
    frame_mos: dict[str, dict[int, list]] = {}
    for i in frame_df.index:
        item = frame_df.loc[i, 'Item']
        if item not in frame_mos:
            frame_mos[item] = {}

        wd = frame_df.loc[i, 'Nominal\nWidth']
        if wd not in frame_mos[item]:
            frame_mos[item][wd] = []

        mo_num = frame_df.loc[i, 'Lot']
        mo_qty = frame_df.loc[i, 'Quantity']
        week = dt.date.fromisoformat(frame_df.loc[i, 'WEEKOF'])
        frame_mos[item][wd].append((mo_num, mo_qty, week))

    for item in frame_mos:
        for wd in frame_mos[item]:
            frame_mos[item][wd] = sorted(frame_mos[item][wd], key=lambda x: x[2])
    
    return insp_mos, frame_mos

def link_mos_orders(mo_df: pd.DataFrame):
    reqs, _ = load_demand(dt.datetime.today(), new_only=False)
    insp, frame = get_fin_and_mos(mo_df)

    mo_data = MOLinkTable(mo=[], process=[], yds_expected=[], item=[],
                          ordered_yds=[], pnum=[], due_date=[])

    for req in reqs:
        if req.item.id not in insp: continue
        mos = insp[req.item.id]

        oviews = sorted(req.orders, key=lambda o: o.due_date)

        o_idx = 0
        mo_idx = 0
        total_prod = 0
        total_req = 0
        while o_idx < len(oviews) and mo_idx < len(mos):
            mo, qty, _ = mos[mo_idx]
            mo_data['mo'].append(mo)
            mo_data['process'].append('INSPECTION')
            mo_data['yds_expected'].append(qty)
            mo_data['item'].append(oviews[o_idx].item.id)
            mo_data['ordered_yds'].append(oviews[o_idx].init_yds)
            mo_data['pnum'].append(oviews[o_idx].pnum)
            mo_data['due_date'].append(oviews[o_idx].due_date)

            if total_prod + qty >= total_req + oviews[o_idx].init_yds:
                total_req += oviews[o_idx].init_yds
                o_idx += 1
            else:
                total_prod += qty
                mo_idx += 1
        
        item_comps = req.item.id.split('-')
        no_width = '-'.join(item_comps[:-1])
        item_wd = float(item_comps[-1])
        if no_width not in frame: continue
        mo_widths = frame[no_width]
        mos = []
        if item_wd*2 in mo_widths:
            for mo, qty, week in mo_widths[item_wd*2]:
                mos.append((mo, qty*2*0.85, week))
        if item_wd*3 in mo_widths:
            for mo, qty, week in mo_widths[item_wd*3]:
                mos.append((mo, qty*3*0.85, week))
        
        mos = sorted(mos, key=lambda x: x[2])
        mo_idx = 0
        while o_idx < len(oviews) and mo_idx < len(mos):
            mo, qty, _ = mos[mo_idx]
            mo_data['mo'].append(mo)
            mo_data['process'].append('FRAME')
            mo_data['yds_expected'].append(qty)
            mo_data['item'].append(oviews[o_idx].item.id)
            mo_data['ordered_yds'].append(oviews[o_idx].init_yds)
            mo_data['pnum'].append(oviews[o_idx].pnum)
            mo_data['due_date'].append(oviews[o_idx].due_date)

            if total_prod + qty >= total_req + oviews[o_idx].init_yds:
                total_req += oviews[o_idx].init_yds
                o_idx += 1
            else:
                total_prod += qty
                mo_idx += 1
    
    return mo_data

def main(fpath: str):
    outpath = os.path.join(os.path.dirname(__file__), 'datasrc', 'mo_links.xlsx')
    writer = pd.ExcelWriter(outpath, datetime_format='MM/DD')
    mo_df = load_1427_report(fpath)
    mo_links = link_mos_orders(mo_df)
    link_df = pd.DataFrame(data=mo_links)
    link_df.to_excel(writer, sheet_name='mo_priorities', index=False,
                     float_format='%.2f')
    writer.close()

if __name__ == '__main__':
    main(sys.argv[1])