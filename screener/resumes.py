"""Read resumes and match each one to a student in the score sheet."""
import re
from pathlib import Path

from pypdf import PdfReader

def extract_text(path):
    """Return all the text in a PDF or TXT resume."""
    path = Path(path)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

def load_resumes(folder):
    """Read every PDF and TXT file in a folder.

    Returns a list like: [{"file": "Aarav_Mehta_Resume.pdf", "text": "..."}, ...]
    A file that can't be read gets empty text, so one bad file doesn't stop the run.
    """
    resumes = []
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() not in (".pdf", ".txt"):
            continue
        try:
            text = extract_text(path)
        except Exception:
            text = ""
        resumes.append({"file": path.name, "text": text})
    return resumes

def words(text):
    """Lower-case words of 2+ letters: 'Aarav_Mehta_Resume.pdf' -> {'aarav', 'mehta', 'resume', 'pdf'}"""
    return set(re.findall(r"[a-z]{2,}", text.lower()))


def match_score(name, resume):
    """Share of the student's name words found in the file name or the top of the resume (0 to 1)."""
    name_words = words(name)
    if not name_words:
        return 0.0
    found = words(resume["file"]) | words(resume["text"][:300])
    return len(name_words & found) / len(name_words)


def match_resumes(names, resumes, threshold=0.5):
    """Pair each student name with their resume.

    Returns (matched, unmatched):
      matched   = {"Aarav Mehta": {"file": ..., "text": ...}, ...}
      unmatched = resumes that matched nobody
    The strongest matches are made first, and each resume is used only once.
    """
    pairs = []
    for name in names:
        for index, resume in enumerate(resumes):
            score = match_score(name, resume)
            if score >= threshold:
                pairs.append((score, name, index))
    pairs.sort(reverse=True)

    matched, used = {}, set()
    for score, name, index in pairs:
        if name in matched or index in used:
            continue
        matched[name] = resumes[index]
        used.add(index)

    unmatched = [r for i, r in enumerate(resumes) if i not in used]
    return matched, unmatched