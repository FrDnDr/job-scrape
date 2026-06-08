// ─── Domain types matching backend Pydantic schemas ───────────────────────────

export interface WarehouseJobPosting {
  source: string;
  source_job_id: string;
  url?: string | null;
  title: string;
  company: string;
  skills: string[];
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
  location?: string | null;
  posted_at?: string | null;
  description: string;
}

export interface JobSearchResponse {
  jobs: WarehouseJobPosting[];
  total?: number;
}

export interface ResumeProfile {
  candidate_name?: string | null;
  resume_text: string;
  skills: string[];
  technologies: string[];
  years_experience?: number | null;
  education_level?: string | null; // "Bachelor's" | "Master's" | "PhD" | etc.
}

export interface MatchResponse {
  match_score: number;
  strengths: string[];
  missing_skills: string[];
  recommendation: string;
  skill_overlap: number; // percentage 0–100
}

export interface LearningRecommendation {
  skill: string;
  priority: "High" | "Medium" | "Low";
  effort: string;
  resources?: string[];
}

export interface AnalyticsResponse {
  top_skills: Array<{ skill?: string; count?: number; [k: string]: unknown }>;
  top_paying_skills: Array<{ skill?: string; average_salary?: number; [k: string]: unknown }>;
  common_technologies: Array<{ technology?: string; count?: number; [k: string]: unknown }>;
  market_trends: Array<{ [k: string]: string | number }>;
  learning_recommendations?: LearningRecommendation[];
}

export type JobSource = "remoteok" | "onlinejobs";

export interface IngestionRequest {
  source?: JobSource;
  query?: string;
  limit?: number;
  remote_only?: boolean;
  experience_level?: "" | "junior" | "mid" | "senior";
  employment_type?: "" | "full-time" | "part-time" | "contract" | "freelance";
  salary_min?: number | null;
  salary_max?: number | null;
}

export interface SourceInfo {
  name: string;
  connector: string;
}

export interface SourcesResponse {
  sources: SourceInfo[];
  default: string;
}

// ─── UI-specific helpers ───────────────────────────────────────────────────────

export interface MetricItem {
  label: string;
  value: string | number;
  trend: string;
  positive?: boolean;
}

export interface RoadmapItem {
  skill: string;
  priority: "High" | "Medium" | "Low";
  effort: string;
  resources?: string[];
}

export type NavSection = "jobs" | "match" | "market" | "roadmap";
