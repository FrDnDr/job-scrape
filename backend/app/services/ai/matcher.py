"""
matcher.py — AI resume-to-job matching engine.

Two-stage matching:
    1. Local scoring using spec-aligned weights (Skills 60%, Experience 25%, Education 15%)
    2. Optional AI enrichment via OpenRouter (DeepSeek / Qwen / Gemini / Claude)

Feature vector is built by preprocessing.feature_generator and included in the
AI prompt to give the model quantitative grounding.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from app.core.config import settings
from app.preprocessing.feature_generator import generate_features
from app.schemas.jobs import MatchResponse, ResumeProfile, WarehouseJobPosting

logger = logging.getLogger(__name__)


# ─── Matching weights (spec: Skills 60%, Experience 25%, Education 15%) ───────

@dataclass(frozen=True)
class MatchWeights:
    skill_weight: float = 0.60
    experience_weight: float = 0.25
    education_weight: float = 0.15


# ─── Education level rank for requirement comparison ─────────────────────────

_EDU_RANK: dict[str, int] = {
    "Self-taught": 0,
    "Associate's": 1,
    "Bachelor's": 2,
    "Master's": 3,
    "PhD": 4,
}

_EDU_REQUIREMENT_PATTERNS = [
    ("phd", "PhD"),
    ("master", "Master's"),
    ("bachelor", "Bachelor's"),
    ("associate", "Associate's"),
    ("degree", "Bachelor's"),
    ("diploma", "Bachelor's"),
]


def _detect_required_education(job_description: str) -> str | None:
    """Scan a job description for education requirement keywords."""
    lower = job_description.lower()
    for keyword, level in _EDU_REQUIREMENT_PATTERNS:
        if keyword in lower:
            return level
    return None


# ─── Learning effort lookup ───────────────────────────────────────────────────

_SKILL_EFFORT: dict[str, str] = {
    "airflow": "3 weeks",
    "aws": "4 weeks",
    "azure": "4 weeks",
    "bigquery": "2 weeks",
    "ci/cd": "2 weeks",
    "dbt": "2 weeks",
    "deep learning": "8 weeks",
    "docker": "2 weeks",
    "elasticsearch": "2 weeks",
    "fastapi": "1 week",
    "gcp": "4 weeks",
    "graphql": "1 week",
    "javascript": "4 weeks",
    "kafka": "3 weeks",
    "kubernetes": "5 weeks",
    "langchain": "2 weeks",
    "llm": "3 weeks",
    "machine learning": "6 weeks",
    "next.js": "2 weeks",
    "postgresql": "2 weeks",
    "python": "4 weeks",
    "react": "3 weeks",
    "redis": "1 week",
    "snowflake": "2 weeks",
    "spark": "4 weeks",
    "sql": "3 weeks",
    "terraform": "3 weeks",
    "typescript": "2 weeks",
}

_DEFAULT_EFFORT = "2 weeks"


def estimate_effort(skill: str) -> str:
    return _SKILL_EFFORT.get(skill.lower(), _DEFAULT_EFFORT)


# ─── Local scorer ─────────────────────────────────────────────────────────────

def score_resume_match(
    profile: ResumeProfile,
    job: WarehouseJobPosting,
    weights: MatchWeights = MatchWeights(),
) -> MatchResponse:
    """
    Score a resume against a job posting using the spec-aligned formula.

    Weights: Skills 60% | Experience 25% | Education 15%
    """
    # Generate feature vector
    required_edu = _detect_required_education(job.description)
    required_years = _extract_required_years(job.description)

    features = generate_features(
        resume_skills=profile.skills,
        job_skills=job.skills,
        resume_years=profile.years_experience,
        resume_education=profile.education_level,
        required_years=required_years,
        required_education=required_edu,
    )

    # ── Skill score (60%) ─────────────────────────────────────────────────────
    skill_score = features.skill_overlap / 100.0 if job.skills else 0.5

    # ── Experience score (25%) ────────────────────────────────────────────────
    if features.experience_met is True:
        experience_score = 1.0
    elif features.experience_met is False:
        # Partial credit proportional to how close they are
        if profile.years_experience and required_years:
            experience_score = min(profile.years_experience / required_years, 1.0) * 0.8
        else:
            experience_score = 0.4
    else:
        # Unknown requirement — give neutral 0.6
        experience_score = 0.6

    # ── Education score (15%) ─────────────────────────────────────────────────
    if features.education_met is True:
        education_score = 1.0
    elif features.education_met is False:
        education_score = 0.3
    else:
        # No requirement stated → neutral 0.7
        education_score = 0.7

    weighted = (
        skill_score * weights.skill_weight
        + experience_score * weights.experience_weight
        + education_score * weights.education_weight
    )
    score = max(0, min(100, round(weighted * 100)))

    if score >= 80:
        recommendation = "Strong match — apply now!"
    elif score >= 65:
        recommendation = "Good fit — tailor your resume to highlight matching skills."
    elif score >= 50:
        recommendation = "Partial match — build missing skills before applying."
    else:
        recommendation = "Skill gap detected — focus on the missing skills below first."

    r_set = {s.lower() for s in profile.skills}
    j_set = {s.lower() for s in job.skills}
    strengths = sorted(r_set & j_set)
    missing = sorted(j_set - r_set)

    return MatchResponse(
        match_score=score,
        strengths=strengths,
        missing_skills=missing,
        recommendation=recommendation,
        skill_overlap=features.skill_overlap,
    )


def _extract_required_years(description: str) -> float | None:
    """Parse minimum years of experience from a job description."""
    import re
    patterns = [
        r"(\d+)\+?\s+years?\s+(?:of\s+)?experience",
        r"minimum\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
    ]
    for pat in patterns:
        m = re.search(pat, description, re.I)
        if m:
            return float(m.group(1))
    return None


# ─── OpenRouter enrichment ────────────────────────────────────────────────────

async def enrich_match_with_openrouter(
    profile: ResumeProfile,
    job: WarehouseJobPosting,
    base_match: MatchResponse,
) -> MatchResponse:
    """
    Enrich the local match result with an AI model via OpenRouter.

    Supported models (configured via OPENROUTER_MODEL env var):
        deepseek/deepseek-chat (default)
        qwen/qwen-2.5-72b-instruct
        google/gemini-flash-1.5
        anthropic/claude-3-haiku
    """
    if not settings.openrouter_api_key:
        logger.info("OpenRouter API key not set — returning local match only.")
        return base_match

    import httpx

    # Build quantitative context
    required_edu = _detect_required_education(job.description)
    required_years = _extract_required_years(job.description)
    features = generate_features(
        resume_skills=profile.skills,
        job_skills=job.skills,
        resume_years=profile.years_experience,
        resume_education=profile.education_level,
        required_years=required_years,
        required_education=required_edu,
    )

    system_prompt = (
        "You are a senior career matching analyst for CareerLens, an AI-powered job intelligence platform. "
        "Analyze the candidate profile against the job requirements and return a JSON match assessment. "
        "Be precise, data-driven, and actionable."
    )

    user_prompt = {
        "candidate_profile": profile.model_dump(),
        "job_posting": {
            "title": job.title,
            "company": job.company,
            "skills_required": job.skills,
            "description_excerpt": job.description[:800],
        },
        "local_match": base_match.model_dump(),
        "feature_vector": features.to_dict(),
        "instructions": (
            "Return strict JSON with these exact keys: "
            "match_score (integer 0-100), "
            "strengths (array of skill strings), "
            "missing_skills (array of skill strings), "
            "recommendation (string, 1-2 sentences, actionable), "
            "skill_overlap (float, percentage). "
            "Use the feature_vector for quantitative grounding. "
            "Do not add extra keys."
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://careerlens.io",
                    "X-Title": "CareerLens — AI Job Intelligence",
                },
                json={
                    "model": settings.openrouter_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_prompt)},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        enriched = MatchResponse.model_validate_json(content)
        logger.info(
            "OpenRouter enriched match: score %d → %d",
            base_match.match_score,
            enriched.match_score,
        )
        return enriched

    except Exception as exc:
        logger.warning("OpenRouter enrichment failed (%s) — using local match.", exc)
        return base_match
