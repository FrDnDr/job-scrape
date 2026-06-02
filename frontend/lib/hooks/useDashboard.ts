// ─── useDashboard — all dashboard data-fetching & state ──────────────────────

"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchAnalytics, fetchJobs } from "../api";
import { sampleAnalytics, sampleJobs } from "../sample-data";
import type {
  AnalyticsResponse,
  IngestionRequest,
  JobSource,
  MatchResponse,
  MetricItem,
  ResumeProfile,
  WarehouseJobPosting,
} from "../types";

const EMPTY_ANALYTICS: AnalyticsResponse = {
  top_skills: [],
  top_paying_skills: [],
  common_technologies: [],
  market_trends: [],
  learning_recommendations: [],
};

export interface DashboardState {
  jobs: WarehouseJobPosting[];
  analytics: AnalyticsResponse;
  profile: ResumeProfile | null;
  matchResult: MatchResponse | null;
  loading: boolean;
  error: string | null;
  usingDemoData: boolean;
  metrics: MetricItem[];
  activeSource: JobSource;
  setProfile: (profile: ResumeProfile) => void;
  setMatchResult: (match: MatchResponse) => void;
  loadData: (opts?: Partial<IngestionRequest>) => Promise<void>;
  setActiveSource: (source: JobSource) => void;
}

export function useDashboard(): DashboardState {
  const [jobs, setJobs] = useState<WarehouseJobPosting[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse>(EMPTY_ANALYTICS);
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingDemoData, setUsingDemoData] = useState(false);
  const [activeSource, setActiveSource] = useState<JobSource>("remoteok");

  const loadData = useCallback(
    async (opts: Partial<IngestionRequest> = {}) => {
      setLoading(true);
      setError(null);
      const source = (opts.source ?? activeSource) as JobSource;
      const query = opts.query ?? "data engineer";
      const limit = opts.limit ?? 20;
      try {
        const [jobsRes, analyticsRes] = await Promise.all([
          fetchJobs(query, source, limit),
          fetchAnalytics(query, source, 50),
        ]);
        setJobs(jobsRes.jobs);
        setAnalytics(analyticsRes);
        setUsingDemoData(false);
      } catch (e) {
        // Backend offline — fall back to demo data with a visible notice
        setJobs(sampleJobs);
        setAnalytics(sampleAnalytics);
        setUsingDemoData(true);
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [activeSource],
  );

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const metrics: MetricItem[] = [
    { label: "Jobs collected", value: jobs.length.toLocaleString(), trend: "live", positive: true },
    {
      label: "Tracked skills",
      value: analytics.top_skills.length,
      trend: `from ${activeSource === "onlinejobs" ? "OnlineJobs.ph" : "RemoteOK"}`,
      positive: true,
    },
    {
      label: "Match score",
      value: matchResult ? `${matchResult.match_score}%` : "—",
      trend: matchResult ? matchResult.recommendation.split(" ").slice(0, 3).join(" ") : "Upload resume",
      positive: matchResult ? matchResult.match_score >= 65 : true,
    },
    {
      label: "Skill overlap",
      value: matchResult ? `${matchResult.skill_overlap.toFixed(0)}%` : "—",
      trend: matchResult ? `${matchResult.strengths.length} matched` : "—",
      positive: true,
    },
  ];

  return {
    jobs,
    analytics,
    profile,
    matchResult,
    loading,
    error,
    usingDemoData,
    metrics,
    activeSource,
    setProfile,
    setMatchResult,
    loadData,
    setActiveSource,
  };
}
