"""
jobs.py — Pydantic schemas for CareerLens data models.

Matches backend models to frontend TypeScript types in lib/types.ts.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# ─── Raw ingestion ────────────────────────────────────────────────────────────

class RawJobPosting(BaseModel):
    source: str
    source_job_id: str
    url: str | None = None
    title: str
    company: str
    skills: list[str] = Field(default_factory=list)
    salary: str | None = None
    location: str | None = None
    posted_at: date | None = None
    description: str


# ─── Warehouse / ETL output ───────────────────────────────────────────────────

class WarehouseJobPosting(BaseModel):
    source: str
    source_job_id: str
    url: str | None = None
    title: str
    company: str
    skills: list[str]
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    location: str | None = None
    posted_at: date | None = None
    description: str


# ─── API request/response models ─────────────────────────────────────────────

class JobSearchResponse(BaseModel):
    jobs: list[WarehouseJobPosting]
    total: int = 0

    def model_post_init(self, __context) -> None:
        if self.total == 0:
            object.__setattr__(self, "total", len(self.jobs))


class IngestionRequest(BaseModel):
    source: Literal["remoteok", "onlinejobs"] = Field(
        default="remoteok",
        description="Job board source to scrape from.",
    )
    query: str = Field(default="data engineer", description="Keyword search query.")
    limit: int = Field(default=20, ge=1, le=100)
    # Scraping filters
    remote_only: bool = Field(default=False, description="Return remote jobs only.")
    experience_level: Literal["", "junior", "mid", "senior"] = Field(
        default="",
        description="Filter by seniority level.",
    )
    employment_type: Literal["", "full-time", "part-time", "contract", "freelance"] = Field(
        default="",
        description="Filter by employment type.",
    )
    salary_min: float | None = Field(default=None, description="Minimum salary filter.")
    salary_max: float | None = Field(default=None, description="Maximum salary filter.")


# ─── Resume ───────────────────────────────────────────────────────────────────

class ResumeMatchRequest(BaseModel):
    resume_text: str
    job: WarehouseJobPosting


class ResumeParseRequest(BaseModel):
    resume_text: str


class ResumeProfile(BaseModel):
    candidate_name: str | None = None
    resume_text: str = ""
    skills: list[str]
    technologies: list[str]
    years_experience: float | None = None
    education_level: str | None = None   # e.g. "Bachelor's", "Master's", "PhD"


# ─── AI Matching ──────────────────────────────────────────────────────────────

class MatchResponse(BaseModel):
    match_score: int                     # 0–100
    strengths: list[str]
    missing_skills: list[str]
    recommendation: str
    skill_overlap: float = 0.0           # percentage of job skills covered


class LearningRecommendation(BaseModel):
    skill: str
    priority: Literal["High", "Medium", "Low"]
    effort: str                          # e.g. "2 weeks"
    resources: list[str] = Field(default_factory=list)


# ─── Analytics ───────────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    top_skills: list[dict]
    top_paying_skills: list[dict]
    common_technologies: list[dict]
    market_trends: list[dict]
    learning_recommendations: list[LearningRecommendation] = Field(default_factory=list)


class ProfileAnalyticsRequest(BaseModel):
    profile: ResumeProfile
    jobs: list[WarehouseJobPosting]
