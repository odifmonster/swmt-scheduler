#!/usr/bin/env python

from typing import NamedTuple, TypedDict, Unpack
import os

def _nth_parent(path: str, n: int) -> os.PathLike:
    res = path
    for _ in range(n):
        res = os.path.dirname(res)
    return res

class InfoKWArgs(TypedDict):
    excel_book: str
    sheet_name: str
    folder: str | None = None
    columns: list[str] | None = None
    column_names: list[str] | None = None
    excel_columns: str | None = None
    start_row: int = 0
    end_row: int | None = None

class ExcelInfo(TypedDict):
    fpath: str = ''
    sheet_name: str = ''
    header: int | None = 0
    skiprows: int = 0
    nrows: int | None = None
    names: list[str] | None = None
    usecols: str | list[str] | None = None

def make_excel_info(**kwargs: Unpack[InfoKWArgs]) -> ExcelInfo:
    create_args = {}
    
    if kwargs['folder'] is None:
        parent = _nth_parent(__file__, 4)
        dirpath = os.path.join(parent, 'datasrc')
    else:
        dirpath = kwargs['folder']
        if not os.path.isdir(dirpath):
            dirpath = os.path.dirname(dirpath)
    
    create_args['fpath'] = os.path.join(dirpath, kwargs['excel_book'])
    create_args['sheet_name'] = kwargs['sheet_name']
    create_args['skiprows'] = kwargs['start_row']

    if not kwargs['column_names'] is None:
        if kwargs['excel_columns'] is None:
            raise ValueError('Cannot provide alternate column names without specifying corresponding columns.')
        
        create_args['names'] = kwargs['column_names']
        create_args['usecols'] = kwargs['excel_columns']
        create_args['header'] = None
    elif not kwargs['columns'] is None:
        create_args['usecols'] = kwargs['columns']
    
    if not kwargs['end_row'] is None:
        create_args['nrows'] = kwargs['end_row'] - kwargs['start_row'] + 1
    
    return ExcelInfo(**create_args)