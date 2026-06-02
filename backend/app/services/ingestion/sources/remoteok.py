import requests

from app.core.config import settings
from app.schemas.jobs import RawJobPosting


class RemoteOKSource:
    source_name = "remoteok"
    endpoint = "https://remoteok.com/api"

    def fetch(self, query: str, limit: int = 20) -> list[RawJobPosting]:
        response = requests.get(
            self.endpoint,
            headers={"User-Agent": settings.remoteok_user_agent},
            timeout=20,
        )
        response.raise_for_status()

        rows = response.json()
        jobs: list[RawJobPosting] = []
        query_lower = query.lower()

        for row in rows:
            if not isinstance(row, dict) or "id" not in row:
                continue

            title = str(row.get("position") or row.get("title") or "").strip()
            description = str(row.get("description") or "").strip()
            company = str(row.get("company") or "Unknown").strip()
            tags = [str(tag) for tag in row.get("tags") or []]
            searchable = f"{title} {description} {company} {' '.join(tags)}".lower()
            if query_lower and query_lower not in searchable:
                continue

            salary = None
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

        return jobs
