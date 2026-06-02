# API Contract

Base URL:

```text
http://localhost:8000
```

## Health

`GET /health`

Returns service status.

## Ingest Jobs

`POST /api/ingest`

```json
{
  "source": "sample",
  "query": "data engineer",
  "limit": 20
}
```

Fetches jobs from a source, normalizes them, stores them in PostgreSQL, and returns the normalized postings.

Supported sources:

- `sample`
- `remoteok`

## Sample Job Search

`GET /api/jobs?query=data&limit=20`

Returns normalized sample jobs without writing to the database.

## Resume Parse

`POST /api/resume/parse-text`

```json
{
  "resume_text": "Jane Candidate\nPython SQL PostgreSQL\n3 years experience"
}
```

Accepts resume text and returns:

```json
{
  "candidate_name": "Jane Candidate",
  "skills": ["python", "sql"],
  "technologies": ["python", "sql"],
  "years_experience": 3
}
```

## Resume Upload

`POST /api/resume/upload`

Accepts `.pdf` or text files as multipart form data.

## Match

`POST /api/match`

```json
{
  "resume_text": "Jane Candidate\nPython SQL PostgreSQL\n3 years experience",
  "job": {
    "source": "sample",
    "source_job_id": "sample-data-engineer-001",
    "url": "https://example.com/jobs/data-engineer",
    "title": "Data Engineer",
    "company": "Northstar Analytics",
    "skills": ["python", "sql", "postgresql", "airflow"],
    "salary_min": 80000,
    "salary_max": 120000,
    "salary_currency": "USD",
    "location": "Remote",
    "posted_at": null,
    "description": "Build ETL pipelines."
  }
}
```

Returns match score, strengths, missing skills, and recommendation.

## Analytics

`GET /api/analytics?query=data&limit=50`

Returns top skills, top-paying skills, common technologies, and trend buckets.
