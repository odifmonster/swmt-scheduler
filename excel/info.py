#!/usr/bin/env python

from typing import TypedDict, Unpack, Literal, Any
import os

from .parser import parse_data_info

type ParsedKey = Literal['fabric_items', 'greige_sizes', 'greige_translation', 'inventory',
                         'adaptive_orders', 'pa_demand_plan', 'jet_info']

INFO_MAP: dict[ParsedKey, 'ExcelInfo'] = {}

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

    @classmethod
    def create(cls, raw: dict[str, Any]) -> 'InfoKWArgs':
        res = {
            'folder': None, 'columns': None, 'column_names': None,
            'excel_columns': None, 'start_row': 0, 'end_row': None
        }
        for key in raw:
            res[key] = raw[key]
        return res

class ExcelInfo(TypedDict):
    fpath: str = ''
    sheet_name: str = ''
    header: int | None = 0
    skiprows: int = 0
    nrows: int | None = None
    names: list[str] | None = None
    usecols: str | list[str] | None = None

class PandasKWArgs(TypedDict, total=False):
    sheet_name: str
    header: int | None
    skiprows: int
    nrows: int | None
    names: list[str] | None
    usecols: str | list[str] | None
    dtype: dict[str, str] | None

class ParsedDataInfo(TypedDict):
    fabric_items: ExcelInfo
    greige_sizes: ExcelInfo
    greige_translation: ExcelInfo
    inventory: ExcelInfo
    adaptive_orders: ExcelInfo
    pa_demand_plan: ExcelInfo
    jet_info: ExcelInfo

def make_excel_info(**kwargs: Unpack[InfoKWArgs]) -> ExcelInfo:
    create_args = {
        'header': 0, 'skiprows': 0, 'nrows': None, 'names': None,
        'usecols': None
    }
    
    if kwargs['folder'] is None:
        parent = _nth_parent(__file__, 2)
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

def init() -> None:
    parent = _nth_parent(__file__, 2)
    fpath = os.path.join(parent, 'data_info.txt')
    raw: dict[ParsedKey, dict[str, Any]] = parse_data_info(fpath)

    parsed: dict[ParsedKey, InfoKWArgs] = {}
    for key in raw:
        parsed[key] = InfoKWArgs.create(raw[key])
        globals()['INFO_MAP'][key] = make_excel_info(**parsed[key])

def get_excel_info(name: ParsedKey) -> tuple[os.PathLike, PandasKWArgs]:
    inf: ExcelInfo = globals()['INFO_MAP'][name]
    res = { k: v for k, v in inf.items() if k != 'fpath' }
    match name:
        case 'fabric_items':
            str_cols = ['GREIGE ITEM', 'STYLE', 'COLOR NAME', 'COLOR NUMBER', 'PA FIN ITEM']
            str_cols += list(map(lambda i: f'JET {i}', (1,2,3,4,7,8,9,10)))
            res['dtype'] = { col: 'string' for col in str_cols }
        case 'greige_sizes':
            res['dtype'] = { 'greige': 'string' }
        case 'greige_translation':
            res['dtype'] = { 'inventory': 'string', 'plan': 'string' }
        case 'jet_info':
            res['dtype'] = { 'jet': 'string', 'alt_jet': 'string' }
        case 'inventory':
            res['dtype'] = { 'Roll': 'string', 'Item': 'string', 'Quality': 'string',
                             'ASSIGNED_ORDER': 'string' }
        case 'adaptive_orders':
            res['dtype'] = { 'Dyelot': 'string', 'Machine': 'string' }
        case 'pa_demand_plan':
            res['dtype'] = { 'PA Fin Item': 'string' }
    return (inf['fpath'], res)