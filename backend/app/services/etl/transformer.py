"""
transformer.py — Normalize raw job postings into warehouse-ready records.

Uses preprocessing modules for:
- HTML stripping (job_cleaner)
- Skill normalization + extraction (skill_normalizer, skill_extractor)
- Salary parsing (salary module)
"""

from app.preprocessing.job_cleaner import clean_description
from app.schemas.jobs import RawJobPosting, WarehouseJobPosting
from app.services.etl.salary import normalize_salary
from app.services.etl.skills import extract_skills


def normalize_job(raw: RawJobPosting) -> WarehouseJobPosting:
    """Transform a single raw job posting into a warehouse-ready record."""
    salary = normalize_salary(raw.salary)
    # Clean description HTML before skill extraction
    clean_desc = clean_description(raw.description)
    skills = extract_skills(clean_desc, raw.skills)

    return WarehouseJobPosting(
        source=raw.source.strip().lower(),
        source_job_id=raw.source_job_id.strip(),
        url=raw.url,
        title=" ".join(raw.title.split()),
        company=" ".join(raw.company.split()),
        skills=skills,
        salary_min=salary.minimum,
        salary_max=salary.maximum,
        salary_currency=salary.currency,
        location=raw.location,
        posted_at=raw.posted_at,
        description=clean_desc,
    )


def normalize_jobs(raw_jobs: list[RawJobPosting]) -> list[WarehouseJobPosting]:
    """Normalize and deduplicate a batch of raw job postings."""
    seen: set[tuple[str, str]] = set()
    normalized: list[WarehouseJobPosting] = []

    for raw in raw_jobs:
        identity = (raw.source.lower(), raw.source_job_id)
        if identity in seen:
            continue
        seen.add(identity)
        normalized.append(normalize_job(raw))

    return normalized
