"""
pipeline.py — Ingestion pipeline: collect → ETL → ready for warehouse.

Supported sources are registered in SOURCES. To add a new source:
    1. Create a connector in app/connectors/
    2. Add it to the SOURCES dict below.

Run independently:
    python -m app.services.ingestion.pipeline --source remoteok --query "data engineer" --limit 20
"""

from __future__ import annotations

import argparse
import logging

from app.connectors.onlinejobs import OnlineJobsConnector
from app.connectors.remoteok import RemoteOKConnector
from app.schemas.jobs import RawJobPosting, WarehouseJobPosting
from app.services.etl.transformer import normalize_jobs

logger = logging.getLogger(__name__)


# ─── Source registry ──────────────────────────────────────────────────────────
# Map source name → connector class

SOURCES: dict[str, type] = {
    "remoteok": RemoteOKConnector,
    "onlinejobs": OnlineJobsConnector,
}


def get_source(source: str):
    """Return an instantiated connector for the given source name."""
    key = source.lower().strip()
    if key not in SOURCES:
        supported = ", ".join(sorted(SOURCES))
        raise ValueError(
            f"Unsupported source '{source}'. Supported sources: {supported}"
        )
    return SOURCES[key]()


def list_sources() -> list[dict[str, str]]:
    """Return metadata about all registered sources."""
    return [
        {"name": name, "connector": cls.__name__}
        for name, cls in sorted(SOURCES.items())
    ]


def collect_raw_jobs(
    source: str,
    query: str,
    limit: int = 20,
    **filters,
) -> list[RawJobPosting]:
    """Fetch raw job postings from the given source."""
    connector = get_source(source)
    return connector.fetch(query=query, limit=limit, **filters)


def collect_jobs(
    source: str,
    query: str,
    limit: int = 20,
    **filters,
) -> list[WarehouseJobPosting]:
    """Collect and ETL-transform job postings from the given source."""
    raw = collect_raw_jobs(source, query, limit, **filters)
    normalized = normalize_jobs(raw)
    logger.info(
        "Pipeline: collected %d raw → %d normalized jobs from '%s'",
        len(raw),
        len(normalized),
        source,
    )
    return normalized


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="CareerLens ingestion pipeline")
    parser.add_argument("--source", default="remoteok", choices=list(SOURCES))
    parser.add_argument("--query", default="data engineer")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    jobs = collect_jobs(args.source, args.query, args.limit)
    print(json.dumps([j.model_dump() for j in jobs], indent=2, default=str))
