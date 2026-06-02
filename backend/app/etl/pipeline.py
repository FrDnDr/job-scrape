"""
pipeline.py — Standalone ETL pipeline for CareerLens.

Orchestrates the full Extract → Transform → Load cycle.

Usage:
    # As a module (production)
    python -m app.etl.pipeline --source onlinejobs --query "data engineer" --limit 50

    # Programmatically
    from app.etl.pipeline import run_etl
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        result = run_etl(source="remoteok", query="python", limit=30, db=db)
        print(f"Loaded {result['loaded']} jobs")
    finally:
        db.close()
"""

from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING

from app.services.ingestion.pipeline import collect_raw_jobs
from app.services.etl.transformer import normalize_jobs

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def run_etl(
    source: str,
    query: str,
    limit: int = 20,
    db: "Session | None" = None,
    **filters,
) -> dict:
    """
    Execute the full ETL pipeline for a given source and query.

    Steps:
        1. Extract  — fetch raw jobs from the connector
        2. Transform — clean HTML, normalize skills + salaries, deduplicate
        3. Load     — upsert into PostgreSQL (if db session provided)

    Args:
        source: Source name (e.g. "remoteok", "onlinejobs")
        query:  Search keyword
        limit:  Max jobs to collect
        db:     SQLAlchemy session; if None, Load step is skipped
        filters: Extra filter kwargs passed to the connector

    Returns:
        dict with keys: raw_count, transformed_count, loaded, skipped
    """
    # ── Extract ───────────────────────────────────────────────────────────────
    logger.info("[ETL] Extract: source=%s query='%s' limit=%d", source, query, limit)
    raw_jobs = collect_raw_jobs(source, query, limit, **filters)
    logger.info("[ETL] Extracted %d raw records", len(raw_jobs))

    # ── Transform ─────────────────────────────────────────────────────────────
    logger.info("[ETL] Transform: normalizing and deduplicating…")
    transformed = normalize_jobs(raw_jobs)
    logger.info("[ETL] %d records after transform/dedup", len(transformed))

    # ── Load ──────────────────────────────────────────────────────────────────
    loaded = 0
    skipped = 0

    if db is not None:
        from app.services.warehouse import upsert_job_posting

        for job in transformed:
            existing = upsert_job_posting(db, job)
            # upsert_job_posting returns the existing row if already present
            # We detect "new" vs "existing" by checking ingested_at was just set
            if existing:
                skipped += 1
            else:
                loaded += 1

        db.commit()
        logger.info("[ETL] Load: %d new | %d skipped (already in warehouse)", loaded, skipped)
    else:
        logger.info("[ETL] No DB session provided — skipping Load step.")

    return {
        "raw_count": len(raw_jobs),
        "transformed_count": len(transformed),
        "loaded": loaded,
        "skipped": skipped,
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    from app.db.session import SessionLocal

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from app.services.ingestion.pipeline import SOURCES
    parser = argparse.ArgumentParser(description="CareerLens ETL pipeline")
    parser.add_argument("--source", default="remoteok", choices=list(SOURCES))
    parser.add_argument("--query", default="data engineer")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--no-db", action="store_true", help="Skip database load step")
    parser.add_argument("--remote-only", action="store_true")
    parser.add_argument("--experience-level", default="", choices=["", "junior", "mid", "senior"])
    args = parser.parse_args()

    filters = {}
    if args.remote_only:
        filters["remote_only"] = True
    if args.experience_level:
        filters["experience_level"] = args.experience_level

    db = None if args.no_db else SessionLocal()
    try:
        result = run_etl(
            source=args.source,
            query=args.query,
            limit=args.limit,
            db=db,
            **filters,
        )
        print(json.dumps(result, indent=2))
    finally:
        if db:
            db.close()
