# Architecture

The platform follows a layered data-engineering architecture.

## Layers

1. Job collection service
   - Source adapters live under `backend/app/services/ingestion/sources`.
   - The initial adapters are `sample` and `remoteok`.
   - New job boards should implement the `JobSource` protocol.

2. ETL service
   - `skills.py` extracts and normalizes known skills.
   - `salary.py` converts salary strings into min/max/currency fields.
   - `transformer.py` deduplicates raw records and emits warehouse-ready postings.

3. Data warehouse
   - SQLAlchemy models are in `backend/app/models/warehouse.py`.
   - PostgreSQL bootstrap SQL is in `scripts/init.sql`.
   - The model separates company, skill, location, job role, and date dimensions from job and resume-match facts.

4. Resume service
   - Parses plain text or PDF resumes.
   - Emits a structured profile with skills, technologies, and years of experience.

5. AI matching service
   - Always returns a deterministic local score.
   - When `OPENROUTER_API_KEY` is set, OpenRouter can refine the score and recommendation.

6. Analytics service
   - Aggregates top skills, top-paying skills, common technologies, and simple trend periods.

7. Dashboard
   - Next.js shell for job exploration, match summaries, market intelligence, and learning recommendations.

## Extension Points

- Add new scrapers by creating a source adapter and registering it in `pipeline.py`.
- Add dbt models after the warehouse schema stabilizes.
- Add Airflow DAGs around the ingestion and transformation entry points.
- Add vector search by storing resume and job embeddings beside the fact tables.
