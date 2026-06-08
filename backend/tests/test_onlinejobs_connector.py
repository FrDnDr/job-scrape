import unittest
from datetime import date

from app.connectors.onlinejobs import OnlineJobsConnector


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class RecordingOnlineJobsConnector(OnlineJobsConnector):
    rate_limit_seconds = 0

    def __init__(self, html: str) -> None:
        self.html = html
        self.requests: list[tuple[str, dict]] = []

    def _get_with_retry(self, url: str, *, headers=None, params=None):
        self.requests.append((url, params or {}))
        return FakeResponse(self.html)


LISTING_HTML = """
<html>
  <body>
    <div class="job-post-details">
      <h4><a href="/jobseekers/job/98765">Senior Python Developer</a></h4>
      <div class="job-salary">PHP 90,000 - 120,000 / month</div>
      <div class="job-description">
        Build Django APIs, automate reports, and maintain PostgreSQL pipelines.
      </div>
      <div class="job-meta">
        <span>Full Time</span>
        <span>Posted on Jan 15, 2026</span>
      </div>
      <div class="job-tags">
        <span class="skill-tag">Python</span>
        <span class="skill-tag">Django</span>
      </div>
    </div>
  </body>
</html>
"""


class OnlineJobsConnectorTests(unittest.TestCase):
    def test_fetch_uses_onlinejobs_search_params_without_employment_filter(self) -> None:
        connector = RecordingOnlineJobsConnector(LISTING_HTML)

        jobs = connector.fetch("python developer", limit=1)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(connector.requests[0][0], connector.base_url)
        self.assertEqual(
            connector.requests[0][1],
            {
                "jobkeyword": "python developer",
                "skill_tags": "",
                "gig": "on",
                "partTime": "on",
                "fullTime": "on",
                "isFromJobsearchForm": "1",
            },
        )

    def test_fetch_maps_employment_filters_to_onlinejobs_params(self) -> None:
        cases = [
            ("full-time", {"fullTime": "on"}),
            ("part-time", {"partTime": "on"}),
            ("contract", {"gig": "on"}),
            ("freelance", {"gig": "on"}),
        ]

        for employment_type, expected_enabled in cases:
            with self.subTest(employment_type=employment_type):
                connector = RecordingOnlineJobsConnector(LISTING_HTML)

                jobs = connector.fetch("assistant", limit=1, employment_type=employment_type)

                self.assertEqual(len(jobs), 1)
                params = connector.requests[0][1]
                self.assertEqual(params["jobkeyword"], "assistant")
                self.assertEqual(params["skill_tags"], "")
                self.assertEqual(params["isFromJobsearchForm"], "1")
                self.assertEqual(
                    {k: v for k, v in params.items() if k in {"gig", "partTime", "fullTime"}},
                    expected_enabled,
                )

    def test_fetch_uses_path_pagination_with_same_search_params(self) -> None:
        html = LISTING_HTML.replace("98765", "98766")
        connector = RecordingOnlineJobsConnector(html)

        jobs = connector.fetch("bookkeeper", limit=2)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(connector.requests[0][0], connector.base_url)
        self.assertEqual(connector.requests[1][0], f"{connector.base_url}/2")
        self.assertNotIn("page", connector.requests[1][1])
        self.assertEqual(connector.requests[1][1]["jobkeyword"], "bookkeeper")

    def test_parse_page_extracts_listing_details(self) -> None:
        connector = OnlineJobsConnector()

        jobs = connector._parse_page(LISTING_HTML, "python")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].source_job_id, "98765")
        self.assertEqual(jobs[0].title, "Senior Python Developer")
        self.assertEqual(jobs[0].url, "https://www.onlinejobs.ph/jobseekers/job/98765")
        self.assertEqual(jobs[0].salary, "PHP 90,000 - 120,000 / month")
        self.assertIn("Build Django APIs", jobs[0].description)
        self.assertIn("Full Time", jobs[0].description)
        self.assertEqual(jobs[0].skills, ["Python", "Django"])
        self.assertEqual(jobs[0].posted_at, date(2026, 1, 15))


if __name__ == "__main__":
    unittest.main()
