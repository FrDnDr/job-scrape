"""
skills.py — ETL skill helpers (delegates to preprocessing modules).

This module re-exports the canonical functions from preprocessing so that
existing callers (warehouse.py, matcher.py) continue to work unchanged.
"""

# Re-export from the preprocessing layer so existing import paths still work
from app.preprocessing.skill_extractor import (  # noqa: F401
    SKILL_CATALOG,
    all_known_skills,
    extract_skills,
    skill_category,
)
from app.preprocessing.skill_normalizer import (  # noqa: F401
    SKILL_ALIASES as _ALIASES,
    normalize_skill,
    normalize_skills,
)
