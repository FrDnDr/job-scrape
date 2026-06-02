from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DimCompany, DimDate, DimJobRole, DimLocation, DimSkill, FactJobPosting
from app.schemas.jobs import WarehouseJobPosting
from app.services.etl.skills import skill_category


def _get_or_create_company(db: Session, name: str) -> DimCompany:
    company = db.scalar(select(DimCompany).where(DimCompany.name == name))
    if company:
        return company
    company = DimCompany(name=name)
    db.add(company)
    db.flush()
    return company


def _get_or_create_skill(db: Session, name: str) -> DimSkill:
    skill = db.scalar(select(DimSkill).where(DimSkill.name == name))
    if skill:
        return skill
    skill = DimSkill(name=name, category=skill_category(name))
    db.add(skill)
    db.flush()
    return skill


def _get_or_create_role(db: Session, title: str) -> DimJobRole:
    title_normalized = title.strip().lower()
    role = db.scalar(select(DimJobRole).where(DimJobRole.title_normalized == title_normalized))
    if role:
        return role

    role_family = "data" if any(token in title_normalized for token in ("data", "analytics")) else None
    seniority = "senior" if "senior" in title_normalized or "lead" in title_normalized else None
    role = DimJobRole(title_normalized=title_normalized, role_family=role_family, seniority=seniority)
    db.add(role)
    db.flush()
    return role


def _get_or_create_date(db: Session, value: date | None) -> DimDate | None:
    if value is None:
        return None
    date_dim = db.scalar(select(DimDate).where(DimDate.calendar_date == value))
    if date_dim:
        return date_dim
    iso = value.isocalendar()
    date_dim = DimDate(
        calendar_date=value,
        year=value.year,
        month=value.month,
        day=value.day,
        week=iso.week,
    )
    db.add(date_dim)
    db.flush()
    return date_dim


def _get_or_create_location(db: Session, location: str | None) -> DimLocation | None:
    if not location:
        return None
    remote_type = "remote" if "remote" in location.lower() else "onsite"
    existing = db.scalar(
        select(DimLocation).where(
            DimLocation.country.is_(None),
            DimLocation.region.is_(None),
            DimLocation.city == location,
            DimLocation.remote_type == remote_type,
        )
    )
    if existing:
        return existing
    location_dim = DimLocation(country=None, region=None, city=location, remote_type=remote_type)
    db.add(location_dim)
    db.flush()
    return location_dim


def upsert_job_posting(db: Session, job: WarehouseJobPosting) -> FactJobPosting:
    existing = db.scalar(
        select(FactJobPosting).where(
            FactJobPosting.source == job.source,
            FactJobPosting.source_job_id == job.source_job_id,
        )
    )
    if existing:
        return existing

    posting = FactJobPosting(
        source=job.source,
        source_job_id=job.source_job_id,
        url=job.url,
        title=job.title,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        company=_get_or_create_company(db, job.company),
        location=_get_or_create_location(db, job.location),
        job_role=_get_or_create_role(db, job.title),
        posted_date=_get_or_create_date(db, job.posted_at),
    )
    posting.skills = [_get_or_create_skill(db, skill) for skill in job.skills]
    db.add(posting)
    db.flush()
    return posting
