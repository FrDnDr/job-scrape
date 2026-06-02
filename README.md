# CareerLens — AI-Powered Job Intelligence Platform

A full-stack data engineering platform that continuously collects **real job postings** from supported job boards, processes and warehouses the data, analyzes labor market trends, and evaluates candidate-job compatibility using AI-powered resume matching.

> **No dummy data. No synthetic datasets.** All insights originate from live job data collected through configurable scraping pipelines.

---

## Architecture

```
Upload Resume (PDF)
       │
       ▼
Resume Processing          ←── app/preprocessing/resume_parser.py
       │
       ▼
Candidate Profile           ←── app/schemas/jobs.py → ResumeProfile
       │
       ▼
Job Collection Pipeline     ←── app/connectors/  (RemoteOK, OnlineJobs.ph)
       │
       ▼
ETL Processing              ←── app/etl/pipeline.py (Extract→Transform→Load)
       │
       ▼
PostgreSQL Warehouse        ←── Star schema: dim_* + fact_job_posting
       │
       ▼
AI Matching Engine          ←── app/services/ai/matcher.py (OpenRouter)
       │
       ▼
Analytics Dashboard         ←── Next.js frontend + Recharts
```

---

## Module Map

| Module | Path | Purpose |
|---|---|---|
| Connectors | `backend/app/connectors/` | Source-specific scrapers (RemoteOK, OnlineJobs.ph) |
| Preprocessing | `backend/app/preprocessing/` | HTML clean, skill normalization, feature vectors |
| ETL | `backend/app/etl/` | Standalone Extract→Transform→Load pipeline |
| Services/ETL | `backend/app/services/etl/` | Salary normalizer, skill extraction |
| Warehouse | `backend/app/services/warehouse.py` | PostgreSQL upsert logic |
| AI Matching | `backend/app/services/ai/matcher.py` | Resume scoring + OpenRouter enrichment |
| Analytics | `backend/app/services/analytics/market.py` | Market intelligence + learning recs |
| Resume | `backend/app/services/resume/parser.py` | PDF + text resume parsing |
| API | `backend/app/api/routes.py` | FastAPI endpoints |
| Frontend | `frontend/` | Next.js dashboard |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- OpenRouter API key (free tier works: https://openrouter.ai)

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env and set:
#   OPENROUTER_API_KEY=your_key_here
#   POSTGRES_PASSWORD=your_secure_password
```

### 2. Start the platform

```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### 3. Run ETL manually (optional)

Inside the backend container:

```bash
# Scrape RemoteOK
docker compose exec backend python -m app.etl.pipeline --source remoteok --query "data engineer" --limit 30

# Scrape OnlineJobs.ph
docker compose exec backend python -m app.etl.pipeline --source onlinejobs --query "python developer" --limit 20

# Remote only, senior level
docker compose exec backend python -m app.etl.pipeline \
  --source remoteok \
  --query "data engineer" \
  --limit 50 \
  --remote-only \
  --experience-level senior
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/sources` | List available job sources |
| `GET` | `/jobs` | Live-scrape jobs (not from DB) |
| `GET` | `/jobs/db` | Jobs stored in PostgreSQL |
| `POST` | `/ingest` | Scrape + persist to warehouse |
| `POST` | `/resume/upload` | Upload PDF resume → profile |
| `POST` | `/resume/parse-text` | Parse text resume → profile |
| `POST` | `/match` | AI resume-to-job matching |
| `GET` | `/analytics` | Market intelligence analytics |
| `POST` | `/analytics/profile` | Personalized learning recommendations |

Full interactive docs at http://localhost:8000/docs

---

## Data Warehouse Schema

```sql
-- Dimensions
dim_company     (id, name, website)
dim_skill       (id, name, category)
dim_location    (id, country, region, city, remote_type)
dim_job_role    (id, title_normalized, role_family, seniority)
dim_date        (id, calendar_date, year, month, day, week)

-- Facts
fact_job_posting   (id, source, source_job_id, title, description,
                    salary_min, salary_max, salary_currency,
                    company_id, location_id, job_role_id, posted_date_id)
fact_resume_match  (id, job_posting_id, candidate_name,
                    match_score, strengths, missing_skills, recommendation)
```

---

## AI Matching Formula

| Signal | Weight |
|---|---|
| Skill coverage | 60% |
| Experience years | 25% |
| Education level | 15% |

AI enrichment via [OpenRouter](https://openrouter.ai) — configurable model:
- `deepseek/deepseek-chat` (default)
- `qwen/qwen-2.5-72b-instruct`
- `google/gemini-flash-1.5`
- `anthropic/claude-3-haiku`

---

## Supported Sources

| Source | Key | Status |
|---|---|---|
| RemoteOK | `remoteok` | ✅ Active (JSON API) |
| OnlineJobs.ph | `onlinejobs` | ✅ Active (HTML scraper) |

Future: WeWorkRemotely, JobStreet, LinkedIn

---

## Technology Stack

**Backend:** Python 3.12, FastAPI, SQLAlchemy, psycopg3, pdfplumber, BeautifulSoup4, httpx  
**Database:** PostgreSQL 16 (star schema)  
**AI:** OpenRouter (DeepSeek / Qwen / Gemini / Claude)  
**Frontend:** Next.js 14, React, TypeScript, Recharts  
**Infrastructure:** Docker Compose  
