"""
market.py — Market analytics engine.

Generates:
- Top skills by demand
- Top paying skills
- Common technologies
- Hiring trends over time
- Personalized learning recommendations (when profile provided)
"""

from __future__ import annotations

from collections import Counter, defaultdict

from app.schemas.jobs import (
    AnalyticsResponse,
    LearningRecommendation,
    ResumeProfile,
    WarehouseJobPosting,
)
from app.services.ai.matcher import estimate_effort


# ─── Priority mapping for missing skills ─────────────────────────────────────

def _learning_priority(skill: str, demand_rank: int) -> str:
    """Assign priority based on how often the skill appears across job listings."""
    if demand_rank <= 3:
        return "High"
    elif demand_rank <= 7:
        return "Medium"
    return "Low"


# ─── Main analytics builder ───────────────────────────────────────────────────

def build_market_analytics(
    jobs: list[WarehouseJobPosting],
    profile: ResumeProfile | None = None,
) -> AnalyticsResponse:
    """
    Build market analytics from a list of job postings.

    Args:
        jobs:    Job postings to analyze.
        profile: Optional candidate profile for personalized recommendations.

    Returns:
        AnalyticsResponse with skill demand, salary, tech, trend, and learning data.
    """
    skill_counts: Counter[str] = Counter()
    skill_salary_totals: defaultdict[str, list[float]] = defaultdict(list)
    trend_counts: Counter[str] = Counter()

    for job in jobs:
        salary_values = [v for v in (job.salary_min, job.salary_max) if v is not None]
        average_salary = sum(salary_values) / len(salary_values) if salary_values else None

        for skill in job.skills:
            skill_counts[skill] += 1
            if average_salary is not None:
                skill_salary_totals[skill].append(average_salary)

        if job.posted_at:
            trend_counts[job.posted_at.isoformat()[:7]] += 1
        else:
            trend_counts["undated"] += 1

    # Top paying skills
    top_paying = []
    for skill, salaries in skill_salary_totals.items():
        if salaries:
            top_paying.append({
                "skill": skill,
                "average_salary": round(sum(salaries) / len(salaries), 2),
            })
    top_paying.sort(key=lambda r: r["average_salary"], reverse=True)

    # Top skills ordered list (for priority mapping)
    top_skills_ordered = skill_counts.most_common(15)

    # Personalized learning recommendations
    recommendations: list[LearningRecommendation] = []
    if profile:
        candidate_skills = {s.lower() for s in profile.skills}
        for rank, (skill, _count) in enumerate(top_skills_ordered, start=1):
            if skill.lower() not in candidate_skills:
                recommendations.append(
                    LearningRecommendation(
                        skill=skill,
                        priority=_learning_priority(skill, rank),
                        effort=estimate_effort(skill),
                        resources=[],
                    )
                )
            if len(recommendations) >= 8:
                break

    return AnalyticsResponse(
        top_skills=[
            {"skill": skill, "count": count}
            for skill, count in skill_counts.most_common(10)
        ],
        top_paying_skills=top_paying[:10],
        common_technologies=[
            {"technology": skill, "count": count}
            for skill, count in skill_counts.most_common(10)
        ],
        market_trends=[
            {"period": period, "job_count": count}
            for period, count in sorted(trend_counts.items())
        ],
        learning_recommendations=recommendations,
    )


def build_profile_recommendations(
    profile: ResumeProfile,
    jobs: list[WarehouseJobPosting],
) -> list[LearningRecommendation]:
    """
    Generate personalized learning recommendations for a candidate.

    Finds skills that appear most frequently in the job set but are absent
    from the candidate's profile, ranked by market demand.
    """
    analytics = build_market_analytics(jobs, profile=profile)
    return analytics.learning_recommendations
