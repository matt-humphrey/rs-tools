# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_read.ipynb.

# %% auto 0
__all__ = ['Metadata', 'unpack_variable_types', 'reformat_metadata', 'read_pyreadstat', 'Dataset', 'read_and_filter_data',
           'combine_dataframes', 'merge_dictionaries']

# %% ../nbs/00_read.ipynb 4
import pandas as pd
import polars as pl
import numpy as np
import pyreadstat
import pyspssio
from pathlib import Path
from typing import Optional, Any
from fastcore.utils import *

from pydantic import BaseModel
from pydantic.dataclasses import dataclass
# from pandera import ...

# %% ../nbs/00_read.ipynb 6
@dataclass
class Metadata:
    label: str
    field_values: dict[int, str]
    field_type: str
    field_width: int
    decimals: int
    variable_type: str

# %% ../nbs/00_read.ipynb 9
def unpack_variable_types(input_dict):
    "..."
    field_type = {}
    decimals = {}
    
    for key, value in input_dict.items():
        if value.startswith('F'):
            field_type[key] = 'Numeric'
            dec = value.split('.')[1]
            decimals[key] = dec if dec != '0' else '0'
        elif value.startswith('DATE'):
            field_type[key] = 'Date'
            decimals[key] = '0'
        elif value.startswith('A'):
            field_type[key] = 'String'
            decimals[key] = '0'
    
    return field_type, decimals

def reformat_metadata(m: pyreadstat.metadata_container, # metadata from pyreadstat
                     ) -> dict[dict[str, Any]]:
    "Reformat metadata into a more readable and consistent format"
    field_type, decimals = unpack_variable_types(m.original_variable_types)
    metadata = {
        "Label": m.column_names_to_labels,
        "Field Type": field_type,
        "Field Width": m.variable_display_width,
        "Decimals": decimals,
        "Variable Type": m.variable_measure,
        "Field Values": m.variable_value_labels
    }
    return metadata

# %% ../nbs/00_read.ipynb 11
def read_pyreadstat(data_dir: str|Path, 
                    file: str, 
                    cols: Optional[list[str]] = None
                    ) -> pl.LazyFrame:
    df, meta = pyreadstat.read_sav(f"{data_dir}/{file}", usecols=cols)
    df = pl.from_pandas(df).lazy()
    return df, meta

# %% ../nbs/00_read.ipynb 12
@dataclass
class Dataset:
    file: str
    data_dir: str | Path
    prefix: Optional[str] = None
    variables: Optional[list[str]] = None

    def load_data(self) -> tuple[pl.LazyFrame, dict[dict[str, Any]]]:
        "Output data and metadata."
        df, meta = read_pyreadstat(self.data_dir, self.file, self.variables)
        meta = reformat_metadata(meta)
        return df, meta
    
        # def strip_prefix(self, df: pl.LazyFrame) -> pl.DataFrame:
    #     stripped_columns = {col: col.replace(self.prefix, "") for col in self.variables}
    #     df = df.rename(stripped_columns)
    #     return df

# %% ../nbs/00_read.ipynb 15
def read_and_filter_data(datasets: list[Dataset]
                         ) -> list[pl.LazyFrame]:
    """
    Take a list of `Dataset`s and return a list of the respective dataframes 
    and metadata for each dataset, filtered for the given columns.
    """
    dataframes = []
    metadata = []
    for ds in datasets:
        df, meta = ds.load_data()
        dataframes.append(df)
        metadata.append(meta)
    return dataframes, metadata

def combine_dataframes(dataframes: list[pl.LazyFrame]
                       ) -> pl.LazyFrame:
    "Take a list of dataframes and return a single, combined dataframe."
    combined_df = dataframes[0]
    for df in dataframes[1:]:
        combined_df = combined_df.join(df, on="ID", how="full", coalesce=True)
    return combined_df

# %% ../nbs/00_read.ipynb 17
from collections import defaultdict

# %% ../nbs/00_read.ipynb 18
def merge_dictionaries(dicts: list[dict[str, Any]]
                       ) -> dict[str, Any]:
    "Merge a series of nested dictionaries."
    merged_dict = defaultdict(dict)
    for d in dicts:
        for key, nested_dict in d.items():
            for nested_key, value in nested_dict.items():
                if nested_key not in merged_dict[key]:
                    merged_dict[key][nested_key] = value
                elif isinstance(value, dict):
                    merged_dict[key][nested_key].update(value)
    return dict(merged_dict)
