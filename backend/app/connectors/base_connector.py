"""
base_connector.py — Abstract base class for all job source connectors.

Every connector must extend BaseConnector and implement:
    source_name : str   — unique identifier used in pipeline routing
    fetch()             — return list[RawJobPosting]

Built-in helpers:
    _get_with_retry()   — HTTP GET with exponential backoff
    _rate_limit()       — polite delay between requests
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Any

import requests
from requests import Response

from app.schemas.jobs import RawJobPosting

logger = logging.getLogger(__name__)


class BaseConnector(abc.ABC):
    """Abstract base for all job board connectors."""

    source_name: str  # Must be set by subclasses
    default_timeout: int = 20
    max_retries: int = 3
    backoff_factor: float = 1.5   # seconds between retries (multiplied each attempt)
    rate_limit_seconds: float = 1.0  # polite delay between paginated requests

    @abc.abstractmethod
    def fetch(self, query: str, limit: int = 20, **filters: Any) -> list[RawJobPosting]:
        """
        Fetch job postings matching the given query.

        Args:
            query:   Keyword search string.
            limit:   Maximum number of postings to return.
            filters: Source-specific optional filter kwargs, e.g.
                     remote_only=True, experience_level="junior".

        Returns:
            List of RawJobPosting records ready for ETL processing.
        """

    # ─── HTTP helpers ─────────────────────────────────────────────────────────

    def _get_with_retry(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Response:
        """
        Perform an HTTP GET with automatic retry on transient failures.

        Raises:
            requests.HTTPError on 4xx / 5xx after all retries are exhausted.
        """
        attempt = 0
        last_exc: Exception | None = None

        while attempt <= self.max_retries:
            try:
                response = requests.get(
                    url,
                    headers=headers or {},
                    params=params,
                    timeout=self.default_timeout,
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                attempt += 1
                if attempt > self.max_retries:
                    break
                wait = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning(
                    "[%s] Request to %s failed (attempt %d/%d): %s — retrying in %.1fs",
                    self.source_name,
                    url,
                    attempt,
                    self.max_retries,
                    exc,
                    wait,
                )
                time.sleep(wait)

        raise RuntimeError(
            f"[{self.source_name}] All {self.max_retries} retries exhausted for {url}"
        ) from last_exc

    def _rate_limit(self) -> None:
        """Sleep for rate_limit_seconds to be polite to the target server."""
        if self.rate_limit_seconds > 0:
            time.sleep(self.rate_limit_seconds)
