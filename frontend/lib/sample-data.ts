// ─── Static sample data used when the backend is offline ──────────────────────

import type { AnalyticsResponse, RoadmapItem, WarehouseJobPosting } from "./types";

export const sampleJobs: WarehouseJobPosting[] = [
  {
    source: "sample",
    source_job_id: "1",
    title: "Data Engineer",
    company: "Northstar Analytics",
    description: "Build and maintain scalable data pipelines using Python and Apache Airflow.",
    skills: ["Python", "SQL", "PostgreSQL", "Airflow", "dbt", "AWS"],
    salary_min: 80000,
    salary_max: 120000,
    salary_currency: "USD",
    location: "Remote",
  },
  {
    source: "sample",
    source_job_id: "2",
    title: "Analytics Engineer",
    company: "Bright Metrics",
    description: "Design data models and transformations in dbt with Snowflake.",
    skills: ["SQL", "dbt", "Snowflake", "Tableau", "Python"],
    salary_min: 90000,
    salary_max: 140000,
    salary_currency: "PHP",
    location: "Philippines Remote",
  },
  {
    source: "sample",
    source_job_id: "3",
    title: "AI Platform Engineer",
    company: "Signal Works",
    description: "Build AI-powered APIs with FastAPI, PostgreSQL, and LLM integrations.",
    skills: ["FastAPI", "PostgreSQL", "OpenRouter", "LLM", "React", "Python"],
    salary_min: 110000,
    salary_max: 150000,
    salary_currency: "USD",
    location: "Remote",
  },
  {
    source: "sample",
    source_job_id: "4",
    title: "ML Engineer",
    company: "Vertex Systems",
    description: "Train and deploy machine learning models at scale.",
    skills: ["Python", "PyTorch", "Kubernetes", "MLflow", "GCP"],
    salary_min: 120000,
    salary_max: 180000,
    salary_currency: "USD",
    location: "San Francisco (Hybrid)",
  },
  {
    source: "sample",
    source_job_id: "5",
    title: "Data Platform Lead",
    company: "Meridian Health",
    description: "Lead a team building the next-generation health data platform.",
    skills: ["Spark", "Databricks", "Python", "SQL", "Azure", "Delta Lake"],
    salary_min: 130000,
    salary_max: 170000,
    salary_currency: "USD",
    location: "Remote",
  },
];

export const sampleAnalytics: AnalyticsResponse = {
  top_skills: [
    { skill: "SQL", count: 34 },
    { skill: "Python", count: 29 },
    { skill: "AWS", count: 21 },
    { skill: "dbt", count: 18 },
    { skill: "Airflow", count: 15 },
    { skill: "Spark", count: 12 },
  ],
  top_paying_skills: [
    { skill: "Kubernetes", avg: 155000 },
    { skill: "PyTorch", avg: 148000 },
    { skill: "Databricks", avg: 142000 },
    { skill: "AWS", avg: 138000 },
    { skill: "Spark", avg: 135000 },
  ],
  common_technologies: [
    { technology: "PostgreSQL", count: 28 },
    { technology: "Snowflake", count: 22 },
    { technology: "Tableau", count: 19 },
    { technology: "Kubernetes", count: 14 },
  ],
  market_trends: [
    { period: "Jan", jobs: 120 },
    { period: "Feb", jobs: 145 },
    { period: "Mar", jobs: 162 },
    { period: "Apr", jobs: 178 },
    { period: "May", jobs: 210 },
    { period: "Jun", jobs: 248 },
  ],
};

export const sampleRoadmap: RoadmapItem[] = [
  { skill: "Airflow", priority: "High", effort: "2 weeks" },
  { skill: "AWS S3 + Glue", priority: "High", effort: "3 weeks" },
  { skill: "dbt Testing", priority: "Medium", effort: "1 week" },
  { skill: "Kubernetes", priority: "Medium", effort: "4 weeks" },
  { skill: "Spark", priority: "Low", effort: "3 weeks" },
];
