from __future__ import annotations

import csv
import json
from pathlib import Path

from linkedin_connector.models import Job
from linkedin_connector.providers.base import JobProvider


class FileJobProvider(JobProvider):
    name = "file"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs: object) -> list[Job]:
        jobs_file_path = kwargs.get("jobs_file_path")
        if not isinstance(jobs_file_path, str) or not jobs_file_path.strip():
            raise ValueError("jobs_file_path is required for the file provider")

        path = Path(jobs_file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"jobs file not found: {path}")

        if path.suffix.lower() == ".json":
            rows = json.loads(path.read_text())
        elif path.suffix.lower() == ".csv":
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
        else:
            raise ValueError("jobs_file_path must point to a .json or .csv file")

        jobs = [self._to_job(row) for row in rows]
        query_text = query.strip().lower()
        location_text = location.strip().lower()

        filtered = []
        for job in jobs:
            query_match = not query_text or query_text in job.title.lower() or query_text in job.company.lower()
            location_match = not location_text or location_text in job.location.lower()
            if query_match and location_match:
                filtered.append(job)

        filtered.sort(key=lambda item: item.score, reverse=True)
        return filtered[:limit]

    @staticmethod
    def _to_job(row: dict[str, object]) -> Job:
        normalized = {str(key): value for key, value in row.items()}
        return Job(
            id=str(normalized.get("id", "")),
            title=str(normalized.get("title", "")),
            company=str(normalized.get("company", "")),
            location=str(normalized.get("location", "")),
            url=str(normalized.get("url", "")),
            recruiter_name=str(normalized.get("recruiter_name", "")),
            recruiter_title=str(normalized.get("recruiter_title", "")),
            hiring_manager_name=str(normalized.get("hiring_manager_name", "")),
            hiring_manager_title=str(normalized.get("hiring_manager_title", "")),
            posted_at=str(normalized.get("posted_at", "")),
            score=float(normalized.get("score", 0.0) or 0.0),
        )
