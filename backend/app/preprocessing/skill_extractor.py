"""
skill_extractor.py — Catalog-driven skill detection from free text.

Detects skills mentioned in job descriptions or resume text using pattern
matching against an extended catalog. Returns normalized, categorized skills.
"""

import re
from collections.abc import Iterable

from app.preprocessing.skill_normalizer import SKILL_ALIASES, normalize_skill


# ─── Extended skill catalog ───────────────────────────────────────────────────
# Category → set of canonical skill names to scan for

SKILL_CATALOG: dict[str, set[str]] = {
    "data": {
        "airflow",
        "analytics engineering",
        "bigquery",
        "dbt",
        "etl",
        "elt",
        "excel",
        "pandas",
        "postgresql",
        "power bi",
        "python",
        "snowflake",
        "spark",
        "sql",
        "tableau",
        "databricks",
        "delta lake",
        "redshift",
        "looker",
        "metabase",
        "superset",
        "dask",
        "polars",
        "sqlalchemy",
    },
    "cloud": {
        "aws",
        "azure",
        "docker",
        "gcp",
        "kubernetes",
        "terraform",
        "s3",
        "lambda",
        "ecs",
        "eks",
        "cloudformation",
        "pulumi",
        "serverless",
    },
    "backend": {
        "api",
        "django",
        "fastapi",
        "flask",
        "graphql",
        "node.js",
        "rest api",
        "spring boot",
        "express",
        "go",
        "rust",
        "java",
        "c#",
        "php",
        "ruby on rails",
        "redis",
        "kafka",
        "elasticsearch",
        "rabbitmq",
    },
    "frontend": {
        "css",
        "html",
        "javascript",
        "next.js",
        "react",
        "recharts",
        "typescript",
        "vue",
        "angular",
        "svelte",
        "tailwind",
        "webpack",
        "vite",
    },
    "ai_ml": {
        "machine learning",
        "deep learning",
        "llm",
        "openrouter",
        "rag",
        "langchain",
        "hugging face",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "mlflow",
        "openai",
        "gemini",
        "claude",
        "deepseek",
        "qwen",
        "gpt",
        "vector database",
        "embeddings",
    },
    "devops": {
        "ci/cd",
        "git",
        "github actions",
        "gitlab ci",
        "jenkins",
        "ansible",
        "linux",
        "bash",
        "nginx",
        "prometheus",
        "grafana",
    },
}


def all_known_skills() -> set[str]:
    """Return the full set of known canonical skill names."""
    return {skill for skills in SKILL_CATALOG.values() for skill in skills}


def skill_category(skill: str) -> str | None:
    """Return the category for a canonical skill name, or None if unknown."""
    normalized = normalize_skill(skill)
    for category, skills in SKILL_CATALOG.items():
        if normalized in skills:
            return category
    return None


def extract_skills(text: str, provided: Iterable[str] | None = None) -> list[str]:
    """
    Extract and normalize skills from free text plus an optional pre-tagged list.

    Process:
    1. Normalize any pre-provided skill tags.
    2. Scan `text` for catalog skills using word-boundary matching.
    3. Scan for aliases and map to canonical names.
    4. Return a sorted, deduplicated list of canonical skill names.

    Args:
        text:     Free-form text (job description, resume, etc.)
        provided: Optional list of raw skill strings already tagged by the source.

    Returns:
        Sorted list of unique canonical skill names found.
    """
    tokens: set[str] = {normalize_skill(s) for s in (provided or []) if s.strip()}

    haystack = f" {text.lower()} "

    # Scan catalog skills
    for skill in all_known_skills():
        escaped = re.escape(skill)
        pattern = rf"(?<![a-z0-9\-]){escaped}(?![a-z0-9\-])"
        if re.search(pattern, haystack):
            tokens.add(skill)

    # Scan aliases → resolve to canonical
    for alias, canonical in SKILL_ALIASES.items():
        escaped = re.escape(alias)
        pattern = rf"(?<![a-z0-9\-]){escaped}(?![a-z0-9\-])"
        if re.search(pattern, haystack):
            tokens.add(canonical)

    return sorted(tokens)
