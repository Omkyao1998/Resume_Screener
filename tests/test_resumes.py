"""Tests for reading resumes and matching them to students."""
from screener.resumes import load_resumes, match_resumes, match_score

NAMES = ["Aarav Mehta", "Diya Nair", "Kabir Joshi", "Meera Iyer", "Rohan Das"]


def test_load_sample_resumes():
    resumes = load_resumes("sample_data/resumes")
    assert len(resumes) == 5
    assert all(len(r["text"]) > 100 for r in resumes)


def test_match_by_file_name():
    resume = {"file": "Aarav_Mehta_Resume.pdf", "text": ""}
    assert match_score("Aarav Mehta", resume) == 1.0


def test_match_by_text_when_file_name_is_useless():
    resume = {"file": "download.pdf", "text": "Rohan Das\nEDUCATION ..."}
    assert match_score("Rohan Das", resume) == 1.0


def test_all_sample_students_matched():
    matched, unmatched = match_resumes(NAMES, load_resumes("sample_data/resumes"))
    assert set(matched) == set(NAMES)
    assert matched["Rohan Das"]["file"] == "download.pdf"
    assert unmatched == []


def test_extra_resume_is_reported_as_unmatched():
    resumes = load_resumes("sample_data/resumes")
    resumes.append({"file": "Unknown_Person.pdf", "text": "Unknown Person"})
    matched, unmatched = match_resumes(NAMES, resumes)
    assert [r["file"] for r in unmatched] == ["Unknown_Person.pdf"]