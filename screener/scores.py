"""Clean the score sheet so the rest of the tool can trust it."""
import re

import pandas as pd

# Subject marks, in the same order as the score sheet
MARK_COLUMNS = [
    "cm1", "maths_ai", "prob_stats",                               # Maths
    "fop", "dsa1", "ada",                                          # DSA
    "intro_aiml", "adv_ml", "ai_tools_business", "deep_learning",  # AI-ML
    "adv_prog", "web_prog",                                        # DEV
    "elective_marks",
]
MOCK_COLUMNS = ["mock_dsa", "mock_dev", "mock_aiml", "mock_core_cs"]
REQUIRED_COLUMNS = ["name", "cgpa"]


def parse_number(value):
    """Turn one cell into (number, starred).

    "72"  -> (72.0, False)
    "40*" -> (40.0, True)
    ""    -> (None, False)
    """
    if pd.isna(value):
        return None, False

    text = str(value).strip()
    if text == "":
        return None, False

    starred = "*" in text
    match = re.search(r"\d+(\.\d+)?", text)
    if match is None:
        return None, starred

    return float(match.group()), starred

def clean_scores(df):
    """Return a cleaned copy of the score sheet.

    - Column names become lower_case_with_underscores
    - Marks, mocks and CGPA become real numbers (blank -> NaN)
    - A new 'starred' column lists subjects that had a '*'
    """
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Score sheet is missing column(s): {', '.join(missing)}")

    # Drop rows with no student name
    df["name"] = df["name"].fillna("").astype(str).str.strip()
    df = df[df["name"] != ""].reset_index(drop=True)

    starred_flags = {}
    for col in MARK_COLUMNS + MOCK_COLUMNS + ["cgpa"]:
        if col not in df.columns:
            continue
        parsed = df[col].map(parse_number)
        df[col] = pd.to_numeric(parsed.map(lambda pair: pair[0]))
        starred_flags[col] = parsed.map(lambda pair: pair[1])

    flags = pd.DataFrame(starred_flags)
    df["starred"] = flags.apply(lambda row: [col for col in row.index if row[col]], axis=1)

    return df