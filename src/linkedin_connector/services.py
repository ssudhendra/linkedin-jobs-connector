from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from linkedin_connector.cache import TTLCache
from linkedin_connector.config import SETTINGS
from linkedin_connector.models import Connection, EnrichedJob, Job, MatchCandidate
from linkedin_connector.providers import DemoJobProvider, FileJobProvider, JobProvider
from linkedin_connector.retry import run_with_retry


class ConnectionRepository:
    def __init__(self) -> None:
        self._cache: TTLCache[list[Connection]] = TTLCache(SETTINGS.cache_ttl_seconds)

    def load_csv(self, csv_path: str) -> list[Connection]:
        path = Path(csv_path).expanduser().resolve()
        cache_key = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if not path.exists():
            raise FileNotFoundError(f"connections file not found: {path}")

        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))

        connections = [self._parse_connection(row) for row in rows]
        self._cache.set(cache_key, connections)
        return connections

    @staticmethod
    def _parse_connection(row: dict[str, str]) -> Connection:
        degree_value = str(row.get("degree", "3")).strip() or "3"
        try:
            degree = max(1, min(3, int(degree_value)))
        except ValueError:
            degree = 3

        return Connection(
            full_name=(row.get("full_name") or "").strip(),
            first_name=(row.get("first_name") or "").strip(),
            last_name=(row.get("last_name") or "").strip(),
            company=(row.get("company") or "").strip(),
            title=(row.get("title") or "").strip(),
            degree=degree,
            profile_url=(row.get("profile_url") or "").strip(),
            email=(row.get("email") or "").strip(),
            location=(row.get("location") or "").strip(),
        )


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, JobProvider] = {
            "demo": DemoJobProvider(),
            "file": FileJobProvider(),
        }

    def get(self, provider_name: str) -> JobProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            supported = ", ".join(sorted(self._providers))
            raise ValueError(f"unsupported provider '{provider_name}'. supported providers: {supported}")
        return provider


class JobSearchService:
    def __init__(self) -> None:
        self._provider_registry = ProviderRegistry()
        self._connection_repository = ConnectionRepository()

    def search_jobs(
        self,
        provider_name: str,
        query: str = "",
        location: str = "",
        limit: int = SETTINGS.default_limit,
        connections_csv_path: str | None = None,
        jobs_file_path: str | None = None,
    ) -> dict[str, object]:
        safe_limit = max(1, min(SETTINGS.max_limit, int(limit)))
        provider = self._provider_registry.get(provider_name)

        jobs = run_with_retry(
            lambda: provider.search_jobs(
                query=query,
                location=location,
                limit=safe_limit,
                jobs_file_path=jobs_file_path,
            ),
            retries=SETTINGS.provider_retries,
        )

        connections = []
        if connections_csv_path:
            connections = self._connection_repository.load_csv(connections_csv_path)

        enriched_jobs = [self._enrich_job(job, connections) for job in jobs]
        return {
            "provider": provider_name,
            "query": query,
            "location": location,
            "limit": safe_limit,
            "result_count": len(enriched_jobs),
            "jobs": [item.to_dict() for item in enriched_jobs],
        }

    def match_connections(self, company: str, recruiter_name: str = "", hiring_manager_name: str = "", connections_csv_path: str = "") -> dict[str, object]:
        connections = self._connection_repository.load_csv(connections_csv_path)
        job = Job(
            id="adhoc",
            title="",
            company=company,
            recruiter_name=recruiter_name,
            hiring_manager_name=hiring_manager_name,
        )
        return self._enrich_job(job, connections).to_dict()

    def _enrich_job(self, job: Job, connections: list[Connection]) -> EnrichedJob:
        company_connections = [item for item in connections if item.company.lower() == job.company.lower()]
        recruiter_matches = self._rank_matches(company_connections, job.recruiter_name, role="recruiter")
        hiring_manager_matches = self._rank_matches(company_connections, job.hiring_manager_name, role="hiring_manager")
        general_matches = self._rank_general_company_matches(company_connections)
        return EnrichedJob(
            job=job,
            recruiter_matches=recruiter_matches,
            hiring_manager_matches=hiring_manager_matches,
            general_company_matches=general_matches,
        )

    def _rank_matches(self, connections: list[Connection], target_name: str, role: str) -> list[MatchCandidate]:
        ranked: list[MatchCandidate] = []
        target_name_normalized = target_name.strip().lower()
        for connection in connections:
            confidence = 0.0
            reasons: list[str] = []
            title_lower = connection.title.lower()
            name_lower = connection.full_name.lower()

            if target_name_normalized and name_lower == target_name_normalized:
                confidence += 0.65
                reasons.append("exact name match")

            if role == "recruiter" and any(term in title_lower for term in ("recruit", "talent", "sourc")):
                confidence += 0.25
                reasons.append("recruiting title match")

            if role == "hiring_manager" and any(term in title_lower for term in ("manager", "director", "head", "lead", "vp")):
                confidence += 0.25
                reasons.append("management title match")

            confidence += self._degree_bonus(connection.degree)
            reasons.append(f"{self._degree_label(connection.degree)} degree proximity")

            if confidence > 0.15:
                ranked.append(
                    MatchCandidate(
                        category=role,
                        confidence=round(min(confidence, 0.99), 2),
                        reason=", ".join(reasons),
                        connection=connection,
                    )
                )

        ranked.sort(key=lambda item: (item.confidence, -item.connection.degree), reverse=True)
        return ranked[:5]

    def _rank_general_company_matches(self, connections: list[Connection]) -> list[MatchCandidate]:
        ranked = [
            MatchCandidate(
                category="company_connection",
                confidence=round(0.35 + self._degree_bonus(connection.degree), 2),
                reason=f"works at target company, degree {connection.degree}",
                connection=connection,
            )
            for connection in connections
        ]
        ranked.sort(key=lambda item: (item.confidence, -item.connection.degree), reverse=True)
        return ranked[:10]

    @staticmethod
    def _degree_bonus(degree: int) -> float:
        mapping = {1: 0.2, 2: 0.12, 3: 0.06}
        return mapping.get(degree, 0.04)

    @staticmethod
    def _degree_label(degree: int) -> str:
        mapping = {1: "1st", 2: "2nd", 3: "3rd"}
        return mapping.get(degree, f"{degree}th")
