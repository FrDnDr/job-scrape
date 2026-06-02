import unittest

from app.schemas.jobs import ResumeProfile, WarehouseJobPosting
from app.services.ai.matcher import score_resume_match
from app.services.resume.parser import parse_resume_text


class MatchingTests(unittest.TestCase):
    def test_parse_resume_text_extracts_profile(self) -> None:
        profile = parse_resume_text(
            "Jane Candidate\nData engineer with 3 years experience using Python, SQL, and PostgreSQL."
        )

        self.assertEqual(profile.candidate_name, "Jane Candidate")
        self.assertEqual(profile.years_experience, 3)
        self.assertTrue({"python", "sql", "postgresql"}.issubset(profile.skills))

    def test_score_resume_match_identifies_strengths_and_gaps(self) -> None:
        profile = ResumeProfile(
            candidate_name="Jane Candidate",
            skills=["python", "sql", "postgresql"],
            technologies=["python", "sql", "postgresql"],
            years_experience=3,
        )
        job = WarehouseJobPosting(
            source="remoteok",
            source_job_id="1",
            title="Data Engineer",
            company="Example Co",
            skills=["python", "sql", "postgresql", "airflow", "aws"],
            salary_min=80000,
            salary_max=120000,
            salary_currency="USD",
            location="Remote",
            description="Build data pipelines.",
        )

        result = score_resume_match(profile, job)

        # New spec weights: Skills 60%, Experience 25%, Education 15%
        # Skill overlap: 3/5 = 60% → skill_score = 0.60
        # Experience: unknown requirement → neutral 0.6 → experience_score = 0.6
        # Education: no requirement stated → neutral 0.7
        # weighted = 0.60*0.60 + 0.6*0.25 + 0.7*0.15 = 0.36 + 0.15 + 0.105 = 0.615 → 62
        self.assertEqual(result.match_score, 62)
        self.assertEqual(result.skill_overlap, 60.0)
        # Strengths should include all 3 overlapping skills
        self.assertEqual(set(result.strengths), {"python", "sql", "postgresql"})
        # Missing should be the 2 job skills not in profile
        self.assertEqual(set(result.missing_skills), {"airflow", "aws"})
        # Score 62 falls in the "Partial match" bracket
        self.assertIn("Partial match", result.recommendation)


if __name__ == "__main__":
    unittest.main()
