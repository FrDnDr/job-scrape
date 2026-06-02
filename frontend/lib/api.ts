// ─── API client — CareerLens backend (FastAPI) ────────────────────────────────

import type {
  AnalyticsResponse,
  IngestionRequest,
  JobSearchResponse,
  LearningRecommendation,
  MatchResponse,
  ResumeProfile,
  SourcesResponse,
  WarehouseJobPosting,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${path} → ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// GET /sources
export function fetchSources(): Promise<SourcesResponse> {
  return request("/sources");
}

// GET /jobs?query=…&source=…&limit=…&remote_only=…&experience_level=…
export function fetchJobs(
  query = "data engineer",
  source = "remoteok",
  limit = 20,
  remoteOnly = false,
  experienceLevel = "",
): Promise<JobSearchResponse> {
  const params = new URLSearchParams({
    query,
    source,
    limit: String(limit),
    remote_only: String(remoteOnly),
    ...(experienceLevel ? { experience_level: experienceLevel } : {}),
  });
  return request(`/jobs?${params}`);
}

// GET /jobs/db?query=…&limit=…  (warehouse DB, not live-scraped)
export function fetchJobsFromDb(query = "", limit = 50): Promise<JobSearchResponse> {
  const params = new URLSearchParams({ query, limit: String(limit) });
  return request(`/jobs/db?${params}`);
}

// POST /ingest
export function ingestJobs(payload: IngestionRequest): Promise<JobSearchResponse> {
  return request("/ingest", { method: "POST", body: JSON.stringify(payload) });
}

// GET /analytics?query=…&source=…&limit=…
export function fetchAnalytics(
  query = "data",
  source = "remoteok",
  limit = 50,
): Promise<AnalyticsResponse> {
  const params = new URLSearchParams({ query, source, limit: String(limit) });
  return request(`/analytics?${params}`);
}

// POST /resume/parse-text
export function parseResumeText(resume_text: string): Promise<ResumeProfile> {
  return request("/resume/parse-text", {
    method: "POST",
    body: JSON.stringify({ resume_text }),
  });
}

// POST /resume/upload (multipart)
export async function uploadResumePdf(file: File): Promise<ResumeProfile> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/resume/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Upload failed (${res.status}): ${detail || "backend unreachable"}`);
  }
  return res.json() as Promise<ResumeProfile>;
}

// POST /match
export function matchResumeToJob(
  resume_text: string,
  job: WarehouseJobPosting,
): Promise<MatchResponse> {
  return request("/match", {
    method: "POST",
    body: JSON.stringify({ resume_text, job }),
  });
}

// POST /analytics/profile
export function fetchProfileRecommendations(
  profile: ResumeProfile,
  jobs: WarehouseJobPosting[],
): Promise<LearningRecommendation[]> {
  return request("/analytics/profile", {
    method: "POST",
    body: JSON.stringify({ profile, jobs }),
  });
}
