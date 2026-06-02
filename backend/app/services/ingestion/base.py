from typing import Protocol

from app.schemas.jobs import RawJobPosting


class JobSource(Protocol):
    source_name: str

    def fetch(self, query: str, limit: int = 20) -> list[RawJobPosting]:
        ...
