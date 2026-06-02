"""
parser.py — Resume parsing service (delegates to preprocessing.resume_parser).

Bridges the preprocessing layer with the Pydantic ResumeProfile schema.
"""

from app.preprocessing.resume_parser import parse_resume_pdf as _parse_pdf
from app.preprocessing.resume_parser import parse_resume_text as _parse_text
from app.schemas.jobs import ResumeProfile


def parse_resume_text(text: str) -> ResumeProfile:
    """Parse a plain-text resume and return a ResumeProfile."""
    parsed = _parse_text(text)
    return ResumeProfile(**parsed)


def parse_resume_pdf(content: bytes) -> ResumeProfile:
    """Parse a PDF resume and return a ResumeProfile."""
    parsed = _parse_pdf(content)
    return ResumeProfile(**parsed)
