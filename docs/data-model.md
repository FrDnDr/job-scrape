# Dimensional Data Model

## Dimensions

`dim_company`

- One row per company name.
- Used for company-level posting counts and salary analysis.

`dim_skill`

- One row per normalized skill.
- Includes a broad category such as `data`, `cloud`, `backend`, `frontend`, or `ai`.

`dim_location`

- One row per location grain.
- The initial model stores simple text locations with a `remote_type`.

`dim_job_role`

- One row per normalized job title.
- Includes early role-family and seniority fields for trend analysis.

`dim_date`

- One row per posting date.
- Supports year, month, day, and ISO week analysis.

## Facts

`fact_job_posting`

- Grain: one unique posting from one source.
- Natural key: `(source, source_job_id)`.
- Measures: salary min, salary max.
- Foreign keys: company, location, job role, posted date.

`job_posting_skill`

- Bridge table between postings and skills.
- Supports many-to-many demand analysis.

`fact_resume_match`

- Grain: one resume-to-job scoring event.
- Measures: match score.
- Attributes: strengths, missing skills, recommendation.
