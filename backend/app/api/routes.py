"""
routes.py — CareerLens API routes.

All routes are mounted at root (no /api prefix).
Frontend calls: /jobs, /ingest, /analytics, /match, /resume/upload, etc.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import (
    AnalyticsResponse,
    IngestionRequest,
    JobSearchResponse,
    LearningRecommendation,
    MatchResponse,
    ProfileAnalyticsRequest,
    ResumeMatchRequest,
    ResumeParseRequest,
    ResumeProfile,
)
from app.services.ai.matcher import enrich_match_with_openrouter, score_resume_match
from app.services.analytics.market import build_market_analytics, build_profile_recommendations
from app.services.ingestion.pipeline import collect_jobs, list_sources
from app.services.resume.parser import parse_resume_pdf, parse_resume_text
from app.services.warehouse import upsert_job_posting

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Source info ──────────────────────────────────────────────────────────────

@router.get("/sources")
def get_sources() -> dict:
    """List all available job data sources and their connector info."""
    return {
        "sources": list_sources(),
        "default": "remoteok",
    }


# ─── Job ingestion ────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=JobSearchResponse)
def ingest_jobs(
    payload: IngestionRequest,
    db: Session = Depends(get_db),
) -> JobSearchResponse:
    """
    Scrape jobs from the specified source and persist to the warehouse.

    Supports filters: remote_only, experience_level, employment_type,
    salary_min, salary_max.
    """
    filters = {}
    if payload.remote_only:
        filters["remote_only"] = True
    if payload.experience_level:
        filters["experience_level"] = payload.experience_level
    if payload.employment_type:
        filters["employment_type"] = payload.employment_type

    try:
        jobs = collect_jobs(payload.source, payload.query, payload.limit, **filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Source unavailable: {exc}") from exc

    for job in jobs:
        upsert_job_posting(db, job)
    db.commit()

    # Apply salary filter post-fetch
    if payload.salary_min is not None:
        jobs = [j for j in jobs if j.salary_min is not None and j.salary_min >= payload.salary_min]
    if payload.salary_max is not None:
        jobs = [j for j in jobs if j.salary_max is not None and j.salary_max <= payload.salary_max]

    return JobSearchResponse(jobs=jobs)


@router.get("/jobs", response_model=JobSearchResponse)
def list_jobs(
    query: str = "data engineer",
    source: str = "remoteok",
    limit: int = 20,
    remote_only: bool = False,
    experience_level: str = "",
) -> JobSearchResponse:
    """Live-scrape jobs from the given source (not from the warehouse DB)."""
    filters = {}
    if remote_only:
        filters["remote_only"] = True
    if experience_level:
        filters["experience_level"] = experience_level

    try:
        jobs = collect_jobs(source, query, limit, **filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Source unavailable: {exc}") from exc

    return JobSearchResponse(jobs=jobs)


@router.get("/jobs/db", response_model=JobSearchResponse)
def list_jobs_from_db(
    query: str = "",
    limit: int = 50,
    db: Session = Depends(get_db),
) -> JobSearchResponse:
    """
    Return jobs stored in the PostgreSQL warehouse.

    Unlike /jobs this does NOT hit external sources — reads only from DB.
    """
    from sqlalchemy import select
    from app.models.warehouse import FactJobPosting
    from app.schemas.jobs import WarehouseJobPosting

    stmt = select(FactJobPosting)
    if query:
        stmt = stmt.where(FactJobPosting.title.ilike(f"%{query}%"))
    stmt = stmt.limit(limit)

    rows = db.scalars(stmt).all()
    jobs = []
    for row in rows:
        try:
            jobs.append(
                WarehouseJobPosting(
                    source=row.source,
                    source_job_id=row.source_job_id,
                    url=row.url,
                    title=row.title,
                    company=row.company.name if row.company else "Unknown",
                    skills=[s.name for s in row.skills],
                    salary_min=row.salary_min,
                    salary_max=row.salary_max,
                    salary_currency=row.salary_currency,
                    location=row.location.city if row.location else None,
                    posted_at=row.posted_date.calendar_date if row.posted_date else None,
                    description=row.description,
                )
            )
        except Exception as exc:
            logger.warning("Skipping malformed DB row %d: %s", row.id, exc)

    return JobSearchResponse(jobs=jobs)


# ─── Resume ───────────────────────────────────────────────────────────────────

@router.post("/resume/parse-text", response_model=ResumeProfile)
def parse_resume_from_text(payload: ResumeParseRequest) -> ResumeProfile:
    """Parse a plain-text resume and return a structured candidate profile."""
    return parse_resume_text(payload.resume_text)


@router.post("/resume/upload", response_model=ResumeProfile)
async def upload_resume(file: UploadFile = File(...)) -> ResumeProfile:
    """Upload a PDF or plain-text resume and return a structured candidate profile."""
    content = await file.read()
    is_pdf = (
        (file.filename and file.filename.lower().endswith(".pdf"))
        or (file.content_type and "pdf" in file.content_type.lower())
    )
    try:
        if is_pdf:
            return parse_resume_pdf(content)
        return parse_resume_text(content.decode("utf-8", errors="ignore"))
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ─── AI Matching ──────────────────────────────────────────────────────────────

@router.post("/match", response_model=MatchResponse)
async def match_resume(payload: ResumeMatchRequest) -> MatchResponse:
    """
    Score a resume against a specific job posting.

    Uses local scoring first, then optionally enriches with OpenRouter AI.
    """
    profile = parse_resume_text(payload.resume_text)
    base_match = score_resume_match(profile, payload.job)
    return await enrich_match_with_openrouter(profile, payload.job, base_match)


# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(
    query: str = "data",
    source: str = "remoteok",
    limit: int = 50,
) -> AnalyticsResponse:
    """Fetch live jobs and compute market analytics."""
    try:
        jobs = collect_jobs(source, query, limit)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return build_market_analytics(jobs)


@router.post("/analytics/profile", response_model=list[LearningRecommendation])
def profile_analytics(payload: ProfileAnalyticsRequest) -> list[LearningRecommendation]:
    """
    Generate personalized learning recommendations for a candidate profile
    based on skill gaps vs the provided job list.
    """
    return build_profile_recommendations(payload.profile, payload.jobs)
