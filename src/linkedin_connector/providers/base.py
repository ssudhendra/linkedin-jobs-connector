from __future__ import annotations

from abc import ABC, abstractmethod

from linkedin_connector.models import Job


class JobProvider(ABC):
    name: str

    @abstractmethod
    def search_jobs(self, query: str, location: str, limit: int, **kwargs: object) -> list[Job]:
        raise NotImplementedError
