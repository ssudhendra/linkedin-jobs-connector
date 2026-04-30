from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Connection:
    full_name: str
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    title: str = ""
    degree: int = 3
    profile_url: str = ""
    email: str = ""
    location: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str = ""
    url: str = ""
    recruiter_name: str = ""
    recruiter_title: str = ""
    hiring_manager_name: str = ""
    hiring_manager_title: str = ""
    posted_at: str = ""
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MatchCandidate:
    category: str
    confidence: float
    reason: str
    connection: Connection

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["connection"] = self.connection.to_dict()
        return result


@dataclass
class EnrichedJob:
    job: Job
    recruiter_matches: list[MatchCandidate] = field(default_factory=list)
    hiring_manager_matches: list[MatchCandidate] = field(default_factory=list)
    general_company_matches: list[MatchCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job": self.job.to_dict(),
            "recruiter_matches": [item.to_dict() for item in self.recruiter_matches],
            "hiring_manager_matches": [item.to_dict() for item in self.hiring_manager_matches],
            "general_company_matches": [item.to_dict() for item in self.general_company_matches],
        }
