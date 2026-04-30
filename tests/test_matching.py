from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from linkedin_connector.auth import LinkedInAuthService
from linkedin_connector.services import JobSearchService


class MatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = JobSearchService()
        self.connections_csv = str(ROOT / "examples" / "connections.csv")
        self.jobs_json = str(ROOT / "examples" / "jobs.json")

    def test_demo_provider_returns_results(self) -> None:
        result = self.service.search_jobs(
            provider_name="demo",
            query="engineer",
            location="Chicago",
            limit=50,
            connections_csv_path=self.connections_csv,
        )
        self.assertGreaterEqual(result["result_count"], 1)
        first_job = result["jobs"][0]
        self.assertTrue(first_job["recruiter_matches"])
        self.assertEqual(first_job["job"]["company"], "Acme Cloud")

    def test_file_provider_works(self) -> None:
        result = self.service.search_jobs(
            provider_name="file",
            query="product manager",
            location="Austin",
            limit=10,
            connections_csv_path=self.connections_csv,
            jobs_file_path=self.jobs_json,
        )
        self.assertEqual(result["result_count"], 1)
        self.assertEqual(result["jobs"][0]["job"]["company"], "Northstar Labs")

    def test_match_connections(self) -> None:
        result = self.service.match_connections(
            company="Acme Cloud",
            recruiter_name="Maya Chen",
            hiring_manager_name="Jordan Patel",
            connections_csv_path=self.connections_csv,
        )
        self.assertGreaterEqual(len(result["recruiter_matches"]), 1)
        self.assertGreaterEqual(len(result["hiring_manager_matches"]), 1)

    def test_auth_status_shape(self) -> None:
        status = LinkedInAuthService().get_status()
        self.assertIn("configured", status)
        self.assertIn("authenticated", status)
        self.assertIn("limitations", status)


if __name__ == "__main__":
    unittest.main()
