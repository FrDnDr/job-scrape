"""
onlinejobs.py — OnlineJobs.ph connector.

OnlineJobs.ph is the primary Philippine remote job board (spec: initial target).

Strategy:
    Scrape the public job listing pages using requests + BeautifulSoup.
    The site uses a standard HTML listing format accessible without login.

Endpoint:
    https://www.onlinejobs.ph/jobseekers/jobsearch

Pagination:
    Appends ?page=N to the URL. We stop when a page returns no jobs or
    the limit is reached.

Rate limiting:
    1.5 seconds between page requests to avoid triggering bot detection.

Error handling:
    On HTTP error or parsing failure, logs the error and returns whatever
    jobs were collected so far (graceful partial results).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.connectors.base_connector import BaseConnector
from app.preprocessing.job_cleaner import clean_description
from app.schemas.jobs import RawJobPosting

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False


class OnlineJobsConnector(BaseConnector):
    source_name = "onlinejobs"
    base_url = "https://www.onlinejobs.ph/jobseekers/jobsearch"
    rate_limit_seconds = 1.5
    max_pages = 5  # cap pages per request to be polite

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def fetch(self, query: str, limit: int = 20, **filters: Any) -> list[RawJobPosting]:
        """
        Scrape OnlineJobs.ph for job postings matching the query.

        Supported filters:
            remote_only (bool)         — filter to remote-tagged jobs
            experience_level (str)     — "junior" | "mid" | "senior"
            employment_type (str)      — "full-time" | "part-time" | "contract"
        """
        if not _BS4_AVAILABLE:
            raise RuntimeError(
                "beautifulsoup4 is required for OnlineJobs.ph scraping. "
                "Run: pip install beautifulsoup4"
            )

        jobs: list[RawJobPosting] = []
        page = 1
        remote_only = filters.get("remote_only", False)
        experience_level = str(filters.get("experience_level", "")).lower()
        employment_type = str(filters.get("employment_type", "")).lower()

        while len(jobs) < limit and page <= self.max_pages:
            params: dict[str, Any] = {"q": query}
            if page > 1:
                params["page"] = page

            try:
                response = self._get_with_retry(
                    self.base_url,
                    headers=self._HEADERS,
                    params=params,
                )
            except Exception as exc:
                logger.warning(
                    "[onlinejobs] Failed fetching page %d for '%s': %s", page, query, exc
                )
                break

            page_jobs = self._parse_page(response.text, query)
            if not page_jobs:
                logger.info("[onlinejobs] No more jobs found on page %d", page)
                break

            # Apply filters
            for job in page_jobs:
                if len(jobs) >= limit:
                    break

                desc_lower = job.description.lower()
                title_lower = job.title.lower()

                if remote_only and "remote" not in desc_lower and "remote" not in (job.location or "").lower():
                    continue

                if experience_level:
                    if experience_level == "junior" and any(
                        w in title_lower for w in ("senior", "lead", "principal")
                    ):
                        continue
                    elif experience_level == "senior" and any(
                        w in title_lower for w in ("junior", "jr", "entry")
                    ):
                        continue

                if employment_type and employment_type not in desc_lower:
                    continue

                jobs.append(job)

            page += 1
            if page <= self.max_pages and len(jobs) < limit:
                self._rate_limit()

        logger.info("[onlinejobs] Collected %d jobs for query '%s'", len(jobs), query)
        return jobs

    def _parse_page(self, html: str, query: str) -> list[RawJobPosting]:
        """Parse a single results page and return RawJobPosting records."""
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[RawJobPosting] = []

        # OnlineJobs.ph job listings are in <div class="job-post-details"> cards
        # or similar containers — we try multiple selectors for resilience.
        cards = (
            soup.select("div.job-post-details")
            or soup.select("div[class*='job-post']")
            or soup.select("article[class*='job']")
            or soup.select("div.job-item")
        )

        if not cards:
            # Fallback: look for any anchor with href containing /jobseekers/job/
            links = soup.select("a[href*='/jobseekers/job/']")
            if not links:
                logger.debug("[onlinejobs] No job cards found on page.")
                return []
            # Build minimal records from link text
            seen: set[str] = set()
            for link in links:
                href = link.get("href", "")
                # Extract job ID from URL like /jobseekers/job/12345
                match = re.search(r"/jobseekers/job/(\d+)", href)
                if not match:
                    continue
                job_id = match.group(1)
                if job_id in seen:
                    continue
                seen.add(job_id)

                title = link.get_text(strip=True) or "Job Opportunity"
                full_url = (
                    href if href.startswith("http")
                    else f"https://www.onlinejobs.ph{href}"
                )
                jobs.append(
                    RawJobPosting(
                        source=self.source_name,
                        source_job_id=job_id,
                        url=full_url,
                        title=title,
                        company="OnlineJobs.ph Employer",
                        skills=[],
                        salary=None,
                        location="Philippines (Remote)",
                        description=title,
                    )
                )
            return jobs

        # Full card parsing
        for card in cards:
            try:
                # Title
                title_el = (
                    card.select_one("h2 a")
                    or card.select_one("h3 a")
                    or card.select_one("a.job-title")
                    or card.select_one("[class*='title'] a")
                    or card.select_one("a")
                )
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                match = re.search(r"/jobseekers/job/(\d+)", href)
                job_id = match.group(1) if match else re.sub(r"\W+", "-", title.lower())[:40]
                full_url = (
                    href if href.startswith("http")
                    else f"https://www.onlinejobs.ph{href}"
                )

                # Company
                company_el = (
                    card.select_one("[class*='company']")
                    or card.select_one("[class*='employer']")
                    or card.select_one("span.employer")
                )
                company = company_el.get_text(strip=True) if company_el else "Philippine Employer"

                # Description
                desc_el = (
                    card.select_one("[class*='desc']")
                    or card.select_one("[class*='detail']")
                    or card.select_one("p")
                )
                description = clean_description(
                    desc_el.get_text(separator=" ", strip=True) if desc_el else title
                )

                # Salary
                salary_el = card.select_one("[class*='salary']") or card.select_one("[class*='pay']")
                salary = salary_el.get_text(strip=True) if salary_el else None

                # Location / tags
                location_el = card.select_one("[class*='location']") or card.select_one("[class*='place']")
                location = location_el.get_text(strip=True) if location_el else "Philippines"

                # Skills from tag pills
                skill_els = card.select("[class*='tag']") or card.select("[class*='skill']")
                skills = [el.get_text(strip=True) for el in skill_els if el.get_text(strip=True)]

                jobs.append(
                    RawJobPosting(
                        source=self.source_name,
                        source_job_id=job_id,
                        url=full_url,
                        title=title,
                        company=company,
                        skills=skills,
                        salary=salary,
                        location=location,
                        description=description or title,
                    )
                )
            except Exception as exc:
                logger.debug("[onlinejobs] Skipping malformed card: %s", exc)
                continue

        return jobs
