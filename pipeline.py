import os
import sys
from datetime import timedelta

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import pandas as pd

import column_calcs as calc
import data_validation as validation


def plot_data(df):
    color_map = {
        'initial': 'red',
        'refill': 'green',
        'reg_collection': 'purple',
        'reg_wd': 'dodgerblue',
        'wd': 'black'
    }

    legend_elements = [
        Line2D([0], [0], color='red', lw=1, label='Initial Storage'),
        Line2D([0], [0], color='green', lw=1, label='Refill Storage Collection'),
        Line2D([0], [0], color='purple', lw=1, label='Regulatory Collection'),
        Line2D([0], [0], color='dodgerblue', lw=1, label='Regulatory Withdrawal'),
        Line2D([0], [0], color='black', lw=1, label='Withdrawal from Storage'),
    ]

    groups = (df['Category'] != df['Category'].shift()).cumsum()

    fig, ax = plt.subplots()

    ax.set_xlabel('Date')
    ax.set_ylabel('Reservoir Volume (acre-feet)')

    ax.plot(df['Date'], df['Reservoir Volume'], color='lightgray', linewidth=1)

    for _, g in df.groupby(groups):
        cat = g['Category'].iloc[0]

        idx = g.index
        start = max(idx.min() - 1, 0)
        segment = df.loc[start:idx.max()]

        ax.plot(segment['Date'], segment['Reservoir Volume'], color=color_map[cat], linewidth=1)

    ax.legend(handles=legend_elements)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
    fig.autofmt_xdate(rotation=30, ha='right')
    print(df['Date'].max() - timedelta(days=30))
    ax.axvspan(mdates.date2num(df['Date'].max() - timedelta(days=30)), mdates.date2num(df['Date'].max()), color='red', alpha=0.25, label="No 30-day lookahead")

    date_fmt = mdates.DateFormatter('%b %d, %Y')
    def format_hover(x, y):
        try:
            return f"Date: {date_fmt(x)} | Value: {y:.2f}"
        except (ValueError, OverflowError):
            return ""

    ax.format_coord = format_hover

    plt.minorticks_on()
    plt.tight_layout()
    fig.canvas.manager.set_window_title('Reservoir Storage Plot')
    plt.show(block=False)


def run_pipeline(df, start_date=None):
    df = calc.storage_change(df)
    df = calc.storage_gain(df)
    df = calc.moving_max_from_start_date(df, start_date)
    df = calc.initial_collection_to_storage(df)
    df = calc.forward_30_day_moving_minimum(df)
    df = calc.positive_delta_s(df)
    df = calc.refill_collection(df)
    df = calc.total_collection_to_storage(df)
    df = calc.regulatory_collection_to_storage(df)
    df = calc.storage_loss(df)
    df = calc.the_rest(df)
    df = calc.category(df)
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


def read_and_validate_file(filepath):
    df = read_file(filepath)
    validation.validate_columns(df)
    df = validation.clean_dataframe(df)
    validation.validate_types(df)
    return df


def process_file(filepath, start_date=None):
    df = read_and_validate_file(filepath)
    return run_pipeline(df, start_date)


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
