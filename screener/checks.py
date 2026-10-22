"""Free, rule-based checks. No AI, no internet: everything runs on the laptop.

Each problem found is a "flag":
    {"level": "stop", "check": "zero_marks", "message": "..."}

Levels:
    stop  -> hard stop: do not send the student until it is fixed or verified
    warn  -> a person should look at it
    info  -> good to know
"""
import pandas as pd

from screener.scores import MARK_COLUMNS, MOCK_COLUMNS

LOW_MARK = 30  # marks at or below this suggest a possible backlog


def flag(level, check, message):
    return {"level": level, "check": check, "message": message}


def check_marks(student):
    """Checks on one student's marks and mock scores (one row of the cleaned sheet)."""
    flags = []
    marks = {col: student[col] for col in MARK_COLUMNS if col in student.index}

    zeros = [col for col, value in marks.items() if value == 0]
    if zeros:
        flags.append(flag("stop", "zero_marks",
                          f"Zero marks in {', '.join(zeros)}: likely failed or pending. Verify with academics."))

    low = [f"{col} ({value:g})" for col, value in marks.items()
           if pd.notna(value) and 0 < value <= LOW_MARK]
    if low:
        flags.append(flag("warn", "low_marks", f"Very low marks, possible backlog: {', '.join(low)}."))

    blanks = [col for col, value in marks.items() if pd.isna(value)]
    if blanks:
        flags.append(flag("warn", "blank_marks",
                          f"No mark recorded for {', '.join(blanks)}. Averages leave these out."))

    for col in student.get("starred", []):
        flags.append(flag("warn", "starred_mark",
                          f"{col} has an asterisk and may not be counted. Ask academics what it means."))

    mocks = [student[col] for col in MOCK_COLUMNS if col in student.index]
    attempted = [m for m in mocks if pd.notna(m) and m > 0]
    if not attempted:
        flags.append(flag("warn", "no_mocks", "No mock interview attempted, so there is no evidence of live performance."))
    elif len(attempted) < len(mocks):
        missing = [col for col in MOCK_COLUMNS if col in student.index and not (student[col] > 0)]
        flags.append(flag("info", "some_mocks_missing", f"Not attempted: {', '.join(missing)}."))

    return flags


def check_duplicate_cgpa(students):
    """Two students with exactly the same CGPA usually means a copy error in the sheet.

    Returns {student name: [flags]} for the students affected.
    """
    result = {}
    for cgpa, group in students.dropna(subset=["cgpa"]).groupby("cgpa"):
        if len(group) < 2:
            continue
        names = group["name"].tolist()
        for name in names:
            others = ", ".join(n for n in names if n != name)
            result[name] = [flag("warn", "duplicate_cgpa",
                                 f"Same CGPA ({cgpa:g}) as {others}. Possible copy error: check the transcript.")]
    return result