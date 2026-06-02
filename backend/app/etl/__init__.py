"""
etl package — Standalone ETL pipeline runnable independently.

Run the full pipeline:
    python -m app.etl.pipeline --source remoteok --query "data engineer" --limit 20

This module orchestrates:
    1. Collect — fetch raw jobs from a source connector
    2. Clean   — strip HTML, normalize whitespace
    3. Transform — normalize skills, salaries, dedup
    4. Load    — upsert into PostgreSQL warehouse
"""
