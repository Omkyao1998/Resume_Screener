"""Tests for reading and cleaning the score sheet."""
import pandas as pd

from screener.scores import clean_scores, parse_number
from screener.sources.local import read_table


def test_parse_plain_number():
    assert parse_number("72") == (72.0, False)


def test_parse_starred_number():
    assert parse_number("40*") == (40.0, True)


def test_parse_blank_cell():
    assert parse_number("") == (None, False)


def test_clean_sample_sheet():
    clean = clean_scores(read_table("sample_data/score_sheet.csv"))

    assert len(clean) == 5
    assert clean["intro_aiml"].dtype == "float64"

    meera = clean[clean["name"] == "Meera Iyer"].iloc[0]
    assert meera["intro_aiml"] == 40
    assert meera["starred"] == ["intro_aiml"]

    rohan = clean[clean["name"] == "Rohan Das"].iloc[0]
    assert pd.isna(rohan["prob_stats"])

    kabir = clean[clean["name"] == "Kabir Joshi"].iloc[0]
    assert kabir["prob_stats"] == 0


def test_missing_cgpa_column_gives_clear_error():
    df = pd.DataFrame({"name": ["A"]})
    try:
        clean_scores(df)
        assert False, "expected an error"
    except ValueError as error:
        assert "cgpa" in str(error)