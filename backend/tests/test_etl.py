import unittest

from app.schemas.jobs import RawJobPosting
from app.services.etl.salary import normalize_salary
from app.services.etl.skills import extract_skills
from app.services.etl.transformer import normalize_jobs


class EtlTests(unittest.TestCase):
    def test_extract_skills_combines_provided_and_description(self) -> None:
        skills = extract_skills(
            "Build SQL pipelines with Postgres, Airflow, Docker, and AWS.",
            provided=["Python"],
        )

        self.assertEqual(skills, ["airflow", "aws", "docker", "postgresql", "python", "sql"])

    def test_normalize_salary_range_with_currency(self) -> None:
        salary = normalize_salary("$80k - $120k")

        self.assertEqual(salary.minimum, 80000)
        self.assertEqual(salary.maximum, 120000)
        self.assertEqual(salary.currency, "USD")

    def test_normalize_jobs_deduplicates_source_identity(self) -> None:
        raw = RawJobPosting(
            source="sample",
            source_job_id="1",
            title=" Data Engineer ",
            company=" Example Co ",
            skills=["SQL"],
            salary="PHP 90000 - 120000",
            location="Remote",
            description="Python SQL PostgreSQL",
        )

        jobs = normalize_jobs([raw, raw])

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].company, "Example Co")
        self.assertEqual(jobs[0].salary_currency, "PHP")
        self.assertEqual(jobs[0].skills, ["postgresql", "python", "sql"])


if __name__ == "__main__":
    unittest.main()
