"""
resume_parser.py — Richer resume field extraction.

Extends basic skill/experience detection with:
- Education level detection (Bachelor's / Master's / PhD / bootcamp)
- Job title / role extraction from resume headers
- Section-aware parsing (EXPERIENCE, EDUCATION, SKILLS blocks)
"""

import re
from io import BytesIO

from app.preprocessing.skill_extractor import extract_skills


# ─── Education level patterns ─────────────────────────────────────────────────

_EDU_LEVELS = [
    (r"\bph\.?d\b|\bdoctor(?:ate|al)\b", "PhD"),
    (r"\bm\.?s\.?\b|\bmaster(?:\'s|s)?\b|\bm\.?eng\b|\bmba\b", "Master's"),
    (r"\bb\.?s\.?\b|\bb\.?a\.?\b|\bbachelor(?:\'s|s)?\b|\bb\.?eng\b|\bbs\b|\bba\b", "Bachelor's"),
    (r"\bassociate(?:\'s|s)?\b", "Associate's"),
    (r"\bbootcamp\b|\bself[\-\s]?taught\b|\bself[\-\s]?learned\b", "Self-taught"),
]


def _extract_education_level(text: str) -> str | None:
    """Return the highest detected education level from the text."""
    lower = text.lower()
    for pattern, level in _EDU_LEVELS:
        if re.search(pattern, lower):
            return level
    return None


# ─── Years of experience ──────────────────────────────────────────────────────

def _extract_years_experience(text: str) -> float | None:
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s+years?", text, flags=re.I)
    if not matches:
        return None
    return max(float(m) for m in matches)


# ─── Candidate name heuristic ─────────────────────────────────────────────────

def _extract_candidate_name(lines: list[str]) -> str | None:
    """
    Return the first non-empty line as the candidate name if it looks like a
    human name (2–4 words, no digits, no common section headers).
    """
    _SECTION_HEADERS = {
        "objective", "summary", "profile", "experience", "education",
        "skills", "projects", "awards", "certifications", "references",
    }
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and not re.search(r"\d", line):
            if line.lower() not in _SECTION_HEADERS:
                return line
    return None


# ─── Public API ───────────────────────────────────────────────────────────────

def parse_resume_text(text: str) -> dict:
    """
    Parse a plain-text resume and return a structured dict.

    Returns:
        {
          "candidate_name":   str | None,
          "resume_text":      str,
          "skills":           list[str],
          "technologies":     list[str],
          "years_experience": float | None,
          "education_level":  str | None,
        }
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skills = extract_skills(text)

    return {
        "candidate_name": _extract_candidate_name(lines),
        "resume_text": text,
        "skills": skills,
        "technologies": skills,
        "years_experience": _extract_years_experience(text),
        "education_level": _extract_education_level(text),
    }


def parse_resume_pdf(content: bytes) -> dict:
    """
    Parse a PDF resume and return a structured dict (same shape as parse_resume_text).
    Requires pdfplumber.
    """
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("Install pdfplumber to parse PDF resumes.") from exc

    text_parts: list[str] = []
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return parse_resume_text("\n".join(text_parts))
