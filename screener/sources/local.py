"""Read input files from the user's computer."""
from pathlib import Path

import pandas as pd


def read_table(path):
    """Read a CSV or Excel file into a table, keeping every cell as text."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, dtype=str)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path, dtype=str)

    raise ValueError(f"Unsupported file type: {suffix}. Use a .csv or .xlsx file.")