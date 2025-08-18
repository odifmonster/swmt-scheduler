from typing import TypedDict, Literal
import os

type ParsedKey = Literal['fabric_items', 'greige_sizes', 'greige_translation', 'inventory',
                         'adaptive_orders', 'pa_demand_plan', 'jet_info']

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

def init() -> None: ...

def get_excel_info(name: ParsedKey) -> tuple[os.PathLike, PandasKWArgs]: ...