from __future__ import annotations

import json
from pathlib import Path

from linkedin_connector.models import Job
from linkedin_connector.providers.base import JobProvider


class DemoJobProvider(JobProvider):
    name = "demo"

    def __init__(self) -> None:
        data_file = Path(__file__).resolve().parents[1] / "data" / "demo_jobs.json"
        self._jobs = [Job(**item) for item in json.loads(data_file.read_text())]

    def search_jobs(self, query: str, location: str, limit: int, **kwargs: object) -> list[Job]:
        query_text = query.strip().lower()
        location_text = location.strip().lower()

        filtered = []
        for job in self._jobs:
            title_text = job.title.lower()
            company_text = job.company.lower()
            job_location = job.location.lower()
            query_match = not query_text or query_text in title_text or query_text in company_text
            location_match = not location_text or location_text in job_location
            if query_match and location_match:
                filtered.append(job)

        filtered.sort(key=lambda item: item.score, reverse=True)
        return filtered[:limit]
