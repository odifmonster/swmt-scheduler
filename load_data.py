#!/usr/bin/env python

import pandas as pd, datetime as dt

from app.schedule import Jet, Job
import excel

excel.init()

fpath, pdargs = excel.get_excel_info('jet_info')
df = pd.read_excel(fpath, **pdargs)

def load_jets(min_date: dt.datetime, max_date: dt.datetime) -> list[Jet]:
    pass

def load_jobs(jets: list[Jet]) -> None:
    job_sheet: pd.DataFrame = pd.read_excel("/Users/oliverwyner/Shawmut/LamDemandPlanning 2.xlsx", sheet_name = 'Adaptive')
    job_sheet['Machine'] = job_sheet['Machine'].astype('string')
    job_sheet['Dyelot'] = job_sheet['Dyelot'].astype('string')
    jet_list=['J-01', 'J-02', 'J-03', 'J-04', 'J-07', 'J-08', 'J-09', 'J-10']
    jet_dict = {'J-01' : "Jet-01", 'J-02' : "Jet-02", 'J-03' : "Jet-03", 'J-04' : "Jet-04", 'J-07' : "Jet-07", 'J-08' : "Jet-08", 'J-09' : "Jet-09", 'J-10' : "Jet-10"}
    for index,row in job_sheet.iterrows():
        if row['Machine'] in jet_list:
            for jet in jets:
                if jet.id == jet_dict[row['Machine']]:
                    if "STRIP" in row['Dyelot']:
                        jet.add_job(Job(row['StartTime'], id= row['Dyelot'],max_date=row['StartTime']+ dt.timedelta(row['CycleTime']),  cycle_time= dt.timedelta(row['CycleTime'])), lots=None)
                    else:
                        jet.add_job(Job(row['StartTime'], id= row['Dyelot'],max_date=row['StartTime']+ dt.timedelta(row['CycleTime']),  cycle_time= dt.timedelta(row['CycleTime'])), lots=tuple())
    
    for jet in jets:
        print(jet.id + "jobs: ")
        for job in list(jet):
            print(job)
        print()