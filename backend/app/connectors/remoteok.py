"""
remoteok.py — RemoteOK connector (refactored to extend BaseConnector).

Fetches from the public RemoteOK JSON API:
    https://remoteok.com/api

Rate limiting: 1 request per API call (single endpoint, no pagination needed).
"""

from __future__ import annotations

import logging
from typing import Any

from app.connectors.base_connector import BaseConnector
from app.core.config import settings
from app.schemas.jobs import RawJobPosting

logger = logging.getLogger(__name__)


class RemoteOKConnector(BaseConnector):
    source_name = "remoteok"
    endpoint = "https://remoteok.com/api"
    rate_limit_seconds = 0.0  # Single request, no need for inter-page delay

    def fetch(self, query: str, limit: int = 20, **filters: Any) -> list[RawJobPosting]:
        """
        Fetch job postings from RemoteOK.

        Supported filters:
            remote_only (bool)         — always True for RemoteOK
            experience_level (str)     — "junior" | "mid" | "senior" (client-side filter)
        """
        try:
            response = self._get_with_retry(
                self.endpoint,
                headers={"User-Agent": settings.remoteok_user_agent},
            )
        except Exception as exc:
            logger.error("[remoteok] Failed to fetch jobs: %s", exc)
            raise

        rows = response.json()
        jobs: list[RawJobPosting] = []
        query_lower = query.lower().strip()

        experience_level = str(filters.get("experience_level", "")).lower()

        for row in rows:
            if not isinstance(row, dict) or "id" not in row:
                continue

            title = str(row.get("position") or row.get("title") or "").strip()
            description = str(row.get("description") or "").strip()
            company = str(row.get("company") or "Unknown").strip()
            tags = [str(tag) for tag in row.get("tags") or []]

            # Keyword filter
            searchable = f"{title} {description} {company} {' '.join(tags)}".lower()
            if query_lower and query_lower not in searchable:
                continue

            # Experience level client-side filter
            if experience_level:
                title_lower = title.lower()
                if experience_level == "junior" and any(
                    w in title_lower for w in ("senior", "lead", "principal", "staff")
                ):
                    continue
                elif experience_level == "senior" and any(
                    w in title_lower for w in ("junior", "jr", "entry")
                ):
                    continue

            salary: str | None = None
            if row.get("salary_min") or row.get("salary_max"):
                salary = f"USD {row.get('salary_min') or ''} - {row.get('salary_max') or ''}"

            jobs.append(
                RawJobPosting(
                    source=self.source_name,
                    source_job_id=str(row["id"]),
                    url=row.get("url"),
                    title=title or "Untitled role",
                    company=company,
                    skills=tags,
                    salary=salary,
                    location=row.get("location") or "Remote",
                    description=description or title,
                )
            )

            if len(jobs) >= limit:
                break

        logger.info("[remoteok] Fetched %d jobs for query '%s'", len(jobs), query)
        return jobs
