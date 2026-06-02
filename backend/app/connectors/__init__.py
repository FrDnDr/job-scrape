"""
connectors package — Source-specific job data connectors.

Each connector is responsible for:
- Fetching job postings from one external platform
- Pagination, retry handling, and rate limiting
- Parsing platform-specific HTML / JSON into RawJobPosting records

Available connectors:
    remoteok    — RemoteOK JSON API
    onlinejobs  — OnlineJobs.ph HTML scraper (primary PH target)

Usage:
    from app.connectors.remoteok import RemoteOKConnector
    from app.connectors.onlinejobs import OnlineJobsConnector
"""
