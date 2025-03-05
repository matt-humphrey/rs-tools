# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_explore.ipynb.

# %% auto 0
__all__ = ['filter_columns', 'unpack_unique_values', 'unique_values', 'filter_metadata']

# %% ../nbs/01_explore.ipynb 4
from .read import *
from pathlib import Path
import polars as pl
import regex as re

# %% ../nbs/01_explore.ipynb 7
def filter_columns(pattern: str,
                   columns: list[str]
                   ) -> list[str]:
    "Return a list of all columns that match a given regex pattern."
    return [col for col in columns if re.search(pattern, col) is not None]

def unpack_unique_values(df: pl.LazyFrame,
                         col: str
                         ) -> tuple[str|int|float]:
    "Return a tuple of the unique values for a given column in a dataframe."
    [vals] = df.select(pl.col(col).unique()).collect().to_dict(as_series=False).values()
    return tuple(vals)

def unique_values(df: pl.LazyFrame,
                  pattern: str
                  ) -> dict[str, set]:
    "Output a tuple of the unique values for each column in a given dataframe that matches the pattern."
    filtered_columns = filter_columns(pattern, df.collect_schema().names())
    return {col: unpack_unique_values(df, col) for col in filtered_columns} 

# %% ../nbs/01_explore.ipynb 10
from collections import defaultdict
from typing import Any
import pandas as pd

# %% ../nbs/01_explore.ipynb 11
def _filter_metadata(m: dict[dict[str, Any]], # metadata nested dict
                    cols: list[str] # list of columns to filter metadata
                    ) -> dict[dict[str, Any]]:
    "Filter metadata from a dataset for the given columns."
    d = defaultdict(dict)

    for key, nested_dicts in m.items():
        for nested_key, value in nested_dicts.items():
            if nested_key in cols:
                d[key][nested_key] = value

    return d

def filter_metadata(pattern: str, # string or regex to filter columns,
                    df: pl.LazyFrame, # merged dataframe,
                    m: dict[dict[str, Any]] # merged metadata
                    ) -> dict[dict[str, Any]]:
    "Filter metadata for given columns that match the provided pattern."
    cols = df.collect_schema().names()
    filtered_columns = filter_columns(pattern, cols)
    filtered_metadata = _filter_metadata(m, filtered_columns)
    return filtered_metadata
