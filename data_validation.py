import warnings

import pandas as pd


CANONICAL_COLUMNS = {
    "Date": {"date", "datetime"},
    "Year": {"year"},
    "Month": {"month"},
    "Reservoir Volume": {"reservoir volume", "reservoir a", "volume", "storage"},
}


def normalize_column_name(column_name):
    return " ".join(str(column_name).strip().lower().replace("_", " ").split())


def rename_to_canonical_columns(df):
    renamed_columns = {}
    used_columns = set()

    for canonical_name, aliases in CANONICAL_COLUMNS.items():
        for original_name in df.columns:
            if original_name in used_columns:
                continue
            if normalize_column_name(original_name) in aliases:
                renamed_columns[original_name] = canonical_name
                used_columns.add(original_name)
                break

    return df.rename(columns=renamed_columns)


def clean_numeric_column(series):
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.strip('"')
        .str.strip("'")
        .str.replace(",", "", regex=False)
        .replace({"": None, "nan": None, "None": None})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_dataframe(df):
    df = rename_to_canonical_columns(df).copy()
    df["Reservoir Volume"] = clean_numeric_column(df["Reservoir Volume"])
    return df


def validate_columns(df):
    normalized_columns = {normalize_column_name(column_name) for column_name in df.columns}
    missing = [
        canonical_name
        for canonical_name, aliases in CANONICAL_COLUMNS.items()
        if normalized_columns.isdisjoint(aliases)
    ]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_types(df):
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df["Date"] = pd.to_datetime(df["Date"])
        except Exception as exc:
            raise ValueError(
                "Column 'Date' must be datetime or convertible to datetime"
            ) from exc

    if not pd.api.types.is_numeric_dtype(df["Year"]):
        try:
            df["Year"] = pd.to_numeric(df["Year"])
        except Exception as exc:
            raise ValueError(
                "Column 'Year' must be numeric or convertible to numeric"
            ) from exc

    if df["Month"].isna().any():
        raise ValueError("Column 'Month' must not contain blank values")

    if not pd.api.types.is_numeric_dtype(df["Reservoir Volume"]):
        try:
            df["Reservoir Volume"] = pd.to_numeric(df["Reservoir Volume"])
        except Exception as exc:
            raise ValueError(
                "Column 'Reservoir Volume' must be numeric or convertible to numeric"
            ) from exc

    if df["Reservoir Volume"].isna().any():
        raise ValueError(
            "Column 'Reservoir Volume' contains blank or non-numeric values after cleaning"
        )
