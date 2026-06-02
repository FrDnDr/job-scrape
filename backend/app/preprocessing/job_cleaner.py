"""
job_cleaner.py — Cleans raw job posting text before further processing.

Responsibilities:
- Strip HTML tags from descriptions
- Normalize whitespace
- Detect and flag near-duplicate jobs (title + company hash)
"""

import hashlib
import re


# ─── HTML stripping ───────────────────────────────────────────────────────────

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_ENTITY_MAP = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&nbsp;": " ",
    "&mdash;": "—",
    "&ndash;": "–",
    "&bull;": "•",
}


def strip_html(text: str) -> str:
    """Remove HTML tags and decode common HTML entities."""
    if not text:
        return ""
    # Decode entities first
    for entity, char in _ENTITY_MAP.items():
        text = text.replace(entity, char)
    # Strip remaining tags
    text = _TAG_RE.sub(" ", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces, tabs, and newlines into single spaces."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def clean_description(description: str) -> str:
    """Full cleaning pipeline: strip HTML → normalize whitespace."""
    return normalize_whitespace(strip_html(description))


# ─── Salary normalization helpers ─────────────────────────────────────────────

_SALARY_NOISE_RE = re.compile(r"[^\d\s\-–—kKmM$₱€£.]+")


def clean_salary_string(salary: str | None) -> str | None:
    """Remove noise from raw salary strings while preserving key tokens."""
    if not salary:
        return None
    return normalize_whitespace(_SALARY_NOISE_RE.sub(" ", salary))


# ─── Deduplication ────────────────────────────────────────────────────────────

def _job_fingerprint(title: str, company: str) -> str:
    """Return a short hash representing the (title, company) identity."""
    key = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """
    Remove near-duplicate job dicts in-place.

    Two jobs are considered duplicates if they share the same (title, company)
    fingerprint *and* the same source.  The first occurrence wins.

    Args:
        jobs: list of dicts each containing at least 'title', 'company', 'source'.

    Returns:
        Deduplicated list preserving original ordering of first occurrences.
    """
    seen: set[str] = set()
    unique: list[dict] = []
    for job in jobs:
        fp = f"{job.get('source', '')}:{_job_fingerprint(job.get('title', ''), job.get('company', ''))}"
        if fp not in seen:
            seen.add(fp)
            unique.append(job)
    return unique
