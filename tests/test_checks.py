"""Tests for the free rule-based checks."""
from screener.checks import check_duplicate_cgpa, check_marks
from screener.scores import add_group_averages, clean_scores
from screener.sources.local import read_table


def sample_students():
    return clean_scores(read_table("sample_data/score_sheet.csv"))


def student(name):
    students = sample_students()
    return students[students["name"] == name].iloc[0]


def checks_for(name):
    return {f["check"] for f in check_marks(student(name))}


def test_group_averages():
    students = add_group_averages(sample_students())
    aarav = students[students["name"] == "Aarav Mehta"].iloc[0]
    rohan = students[students["name"] == "Rohan Das"].iloc[0]
    assert aarav["maths_avg"] == 71.0
    assert rohan["maths_avg"] == 49.5  # blank prob_stats is skipped


def test_clean_student_has_no_flags():
    assert check_marks(student("Aarav Mehta")) == []


def test_zero_marks_are_a_hard_stop():
    flags = check_marks(student("Kabir Joshi"))
    zero = [f for f in flags if f["check"] == "zero_marks"][0]
    assert zero["level"] == "stop"
    assert "prob_stats" in zero["message"]


def test_low_marks_starred_and_blank():
    assert "low_marks" in checks_for("Kabir Joshi")      # ada = 27
    assert "starred_mark" in checks_for("Meera Iyer")    # intro_aiml = 40*
    assert "blank_marks" in checks_for("Rohan Das")      # prob_stats blank


def test_mock_checks():
    assert "no_mocks" in checks_for("Rohan Das")             # all four mocks 0
    assert "some_mocks_missing" in checks_for("Kabir Joshi")  # two mocks 0


def test_duplicate_cgpa():
    result = check_duplicate_cgpa(sample_students())
    assert set(result) == {"Meera Iyer", "Rohan Das"}