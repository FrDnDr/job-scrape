CREATE TABLE IF NOT EXISTS dim_company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    website VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dim_skill (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) UNIQUE NOT NULL,
    category VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS dim_location (
    id SERIAL PRIMARY KEY,
    country VARCHAR(120),
    region VARCHAR(120),
    city VARCHAR(120),
    remote_type VARCHAR(80) NOT NULL DEFAULT 'unspecified',
    CONSTRAINT uq_location_grain UNIQUE (country, region, city, remote_type)
);

CREATE TABLE IF NOT EXISTS dim_job_role (
    id SERIAL PRIMARY KEY,
    title_normalized VARCHAR(255) UNIQUE NOT NULL,
    role_family VARCHAR(120),
    seniority VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS dim_date (
    id SERIAL PRIMARY KEY,
    calendar_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    week INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_job_posting (
    id SERIAL PRIMARY KEY,
    source VARCHAR(120) NOT NULL,
    source_job_id VARCHAR(255) NOT NULL,
    url VARCHAR(1000),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    salary_min DOUBLE PRECISION,
    salary_max DOUBLE PRECISION,
    salary_currency VARCHAR(12),
    company_id INTEGER NOT NULL REFERENCES dim_company(id),
    location_id INTEGER REFERENCES dim_location(id),
    job_role_id INTEGER REFERENCES dim_job_role(id),
    posted_date_id INTEGER REFERENCES dim_date(id),
    ingested_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_job_source_identity UNIQUE (source, source_job_id)
);

CREATE TABLE IF NOT EXISTS job_posting_skill (
    job_posting_id INTEGER NOT NULL REFERENCES fact_job_posting(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES dim_skill(id) ON DELETE CASCADE,
    PRIMARY KEY (job_posting_id, skill_id)
);

CREATE TABLE IF NOT EXISTS fact_resume_match (
    id SERIAL PRIMARY KEY,
    job_posting_id INTEGER NOT NULL REFERENCES fact_job_posting(id),
    candidate_name VARCHAR(255),
    match_score DOUBLE PRECISION NOT NULL,
    strengths TEXT NOT NULL DEFAULT '[]',
    missing_skills TEXT NOT NULL DEFAULT '[]',
    recommendation TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
