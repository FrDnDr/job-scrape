"""
skill_normalizer.py — Canonical skill name resolution.

Examples:
    "postgres"     → "postgresql"
    "pg"           → "postgresql"
    "js"           → "javascript"
    "k8s"          → "kubernetes"
    "tf"           → "terraform"
"""

import re


# ─── Canonical skill catalog ──────────────────────────────────────────────────
# Maps every known alias (lowercase, stripped) → canonical name.

SKILL_ALIASES: dict[str, str] = {
    # PostgreSQL
    "postgres": "postgresql",
    "pg": "postgresql",
    "postgresql": "postgresql",
    "psql": "postgresql",
    # Python
    "python3": "python",
    "python2": "python",
    "py": "python",
    # JavaScript
    "js": "javascript",
    "javascript": "javascript",
    "es6": "javascript",
    "es2015": "javascript",
    # TypeScript
    "ts": "typescript",
    "typescript": "typescript",
    # Node.js
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    # Next.js
    "nextjs": "next.js",
    "next.js": "next.js",
    # React
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    # Kubernetes
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    # Docker
    "docker": "docker",
    "dockerfile": "docker",
    # AWS
    "aws": "aws",
    "amazon web services": "aws",
    # GCP
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    # Azure
    "azure": "azure",
    "microsoft azure": "azure",
    # dbt
    "dbt": "dbt",
    "data build tool": "dbt",
    # Airflow
    "airflow": "airflow",
    "apache airflow": "airflow",
    # Spark
    "spark": "spark",
    "apache spark": "spark",
    "pyspark": "spark",
    # SQL
    "sql": "sql",
    "mysql": "mysql",
    "mssql": "sql server",
    "ms sql": "sql server",
    "sql server": "sql server",
    "t-sql": "sql",
    "tsql": "sql",
    "plsql": "sql",
    # BigQuery
    "bigquery": "bigquery",
    "bq": "bigquery",
    # Snowflake
    "snowflake": "snowflake",
    # Terraform
    "tf": "terraform",
    "terraform": "terraform",
    # Large Language Models
    "llm": "llm",
    "large language model": "llm",
    "large language models": "llm",
    # FastAPI
    "fastapi": "fastapi",
    "fast api": "fastapi",
    # Machine Learning
    "ml": "machine learning",
    "machine learning": "machine learning",
    # Deep Learning
    "dl": "deep learning",
    "deep learning": "deep learning",
    # CI/CD
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "ci cd": "ci/cd",
    # REST API
    "rest": "rest api",
    "restful": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    # GraphQL
    "graphql": "graphql",
    "gql": "graphql",
    # Power BI
    "power bi": "power bi",
    "powerbi": "power bi",
    # Tableau
    "tableau": "tableau",
    # Excel
    "excel": "excel",
    "microsoft excel": "excel",
    "ms excel": "excel",
    # Pandas
    "pandas": "pandas",
    "pd": "pandas",
    # Redis
    "redis": "redis",
    # Elasticsearch
    "elasticsearch": "elasticsearch",
    "elastic": "elasticsearch",
    "es": "elasticsearch",
    # Kafka
    "kafka": "kafka",
    "apache kafka": "kafka",
}


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_skill(skill: str) -> str:
    """
    Resolve a raw skill string to its canonical name.

    Returns the canonical form if a mapping exists, otherwise returns the
    skill lowercased and whitespace-collapsed.
    """
    cleaned = _WHITESPACE_RE.sub(" ", skill.strip().lower())
    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skills(skills: list[str]) -> list[str]:
    """
    Normalize a list of skill strings, deduplicate, and sort.

    Returns a sorted list of unique canonical skill names.
    """
    seen: set[str] = set()
    result: list[str] = []
    for skill in skills:
        canonical = normalize_skill(skill)
        if canonical and canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return sorted(result)
