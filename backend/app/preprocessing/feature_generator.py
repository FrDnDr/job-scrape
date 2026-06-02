"""
feature_generator.py — Generates structured matching feature vectors.

These features are used as enriched context for the AI matching engine,
providing quantitative signals beyond raw text.

Output example:
    {
        "shared_skills":      8,
        "missing_skills":     3,
        "extra_skills":       5,
        "skill_overlap":      72.7,
        "experience_met":     true,
        "education_met":      null,
        "total_job_skills":   11,
        "total_resume_skills": 13,
    }
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


# ─── Education ordering for requirement matching ──────────────────────────────

_EDU_RANK: dict[str, int] = {
    "Self-taught": 0,
    "Associate's": 1,
    "Bachelor's": 2,
    "Master's": 3,
    "PhD": 4,
}


@dataclass
class MatchFeatures:
    shared_skills: int
    missing_skills: int
    extra_skills: int
    skill_overlap: float          # percentage of job skills covered by resume
    experience_met: bool | None   # None if requirement unknown
    education_met: bool | None    # None if requirement unknown
    total_job_skills: int
    total_resume_skills: int

    def to_dict(self) -> dict:
        return asdict(self)


def generate_features(
    resume_skills: list[str],
    job_skills: list[str],
    resume_years: float | None = None,
    resume_education: str | None = None,
    required_years: float | None = None,
    required_education: str | None = None,
) -> MatchFeatures:
    """
    Compute quantitative matching features for a resume vs a job posting.

    Args:
        resume_skills:      Canonical skill names from the candidate's resume.
        job_skills:         Canonical skill names required by the job.
        resume_years:       Candidate's years of experience (or None).
        resume_education:   Candidate's education level string (or None).
        required_years:     Job's minimum years of experience (or None).
        required_education: Job's minimum education requirement (or None).

    Returns:
        MatchFeatures dataclass.
    """
    r_set = {s.lower() for s in resume_skills}
    j_set = {s.lower() for s in job_skills}

    shared = r_set & j_set
    missing = j_set - r_set
    extra = r_set - j_set

    overlap = (len(shared) / len(j_set) * 100) if j_set else 0.0

    # Experience check
    if resume_years is not None and required_years is not None:
        experience_met: bool | None = resume_years >= required_years
    else:
        experience_met = None

    # Education check
    if resume_education and required_education:
        r_rank = _EDU_RANK.get(resume_education, -1)
        req_rank = _EDU_RANK.get(required_education, -1)
        education_met: bool | None = r_rank >= req_rank if r_rank >= 0 and req_rank >= 0 else None
    else:
        education_met = None

    return MatchFeatures(
        shared_skills=len(shared),
        missing_skills=len(missing),
        extra_skills=len(extra),
        skill_overlap=round(overlap, 1),
        experience_met=experience_met,
        education_met=education_met,
        total_job_skills=len(j_set),
        total_resume_skills=len(r_set),
    )
