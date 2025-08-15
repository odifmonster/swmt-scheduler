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
    