import os
import sys

import pandas as pd

import column_calcs as calc
import data_validation as validation


def run_pipeline(df):
    df = calc.storage_change(df)
    df = calc.storage_gain(df)
    df = calc.moving_max_from_start_date(df)
    df = calc.initial_collection_to_storage(df)
    df = calc.forward_30_day_moving_minimum(df)
    df = calc.positive_delta_s(df)
    df = calc.refill_collection(df)
    df = calc.total_collection_to_storage(df)
    df = calc.regulatory_collection_to_storage(df)
    df = calc.storage_loss(df)
    df = calc.the_rest(df)
    df = reorder_output_columns(df)
    return df


def reorder_output_columns(df):
    columns = list(df.columns)
    if 'Storage Loss' not in columns or 'WD' not in columns:
        return df

    columns.remove('Storage Loss')
    wd_index = columns.index('WD')
    columns.insert(wd_index, 'Storage Loss')
    return df[columns]


def process_file(filepath):
    df = read_file(filepath)
    validation.validate_columns(df)
    df = validation.clean_dataframe(df)
    validation.validate_types(df)
    return run_pipeline(df)


def write_output(df, output_path='CALCULATED_DATA.csv'):
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', None)
    df.to_csv(output_path, index=False)


def read_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'File not found: {filepath}')

    extension = os.path.splitext(filepath)[1].lower()
    if extension not in {'.csv', '.xlsx'}:
        raise ValueError(f'Unsupported file type: {filepath}')

    try:
        if extension == '.csv':
            df = pd.read_csv(filepath)
        else:
            try:
                import openpyxl  # noqa: F401
            except ImportError as exc:
                raise ValueError(
                    "Failed to read input file: Excel support requires 'openpyxl' in the active Python "
                    f"environment.\nPython: {sys.executable}\nInstall with: {sys.executable} -m pip install openpyxl"
                ) from exc

            df = pd.read_excel(filepath, engine='openpyxl')
    except Exception as exc:
        if isinstance(exc, ValueError) and str(exc).startswith('Failed to read input file:'):
            raise
        raise ValueError(f'Failed to read input file: {exc}') from exc

    return df
