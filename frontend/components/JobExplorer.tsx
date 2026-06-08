"use client";

import { ArrowUpDown, Filter, Search, X } from "lucide-react";
import { useState } from "react";
import JobCard, { formatSalary } from "./JobCard";
import type { IngestionRequest, JobSource, WarehouseJobPosting } from "../lib/types";

interface JobExplorerProps {
  jobs: WarehouseJobPosting[];
  matchScores?: Record<string, number>;
  activeSource?: JobSource;
  onSourceChange?: (source: JobSource) => void;
  onSearch?: (opts: Partial<IngestionRequest>) => void;
  loading?: boolean;
}

const SOURCE_LABELS: Record<JobSource, string> = {
  remoteok: "RemoteOK",
  onlinejobs: "OnlineJobs.ph",
};

export default function JobExplorer({
  jobs,
  matchScores = {},
  activeSource = "remoteok",
  onSourceChange,
  onSearch,
  loading = false,
}: JobExplorerProps) {
  const [query, setQuery] = useState("");
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<"default" | "salary" | "match">("default");
  const [selected, setSelected] = useState<WarehouseJobPosting | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Filter state
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [experienceLevel, setExperienceLevel] = useState<"" | "junior" | "mid" | "senior">("");
  const [employmentType, setEmploymentType] = useState<"" | "full-time" | "part-time" | "contract" | "freelance">("");

  const toggleSave = (id: string) =>
    setSaved((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  const cycleSort = () =>
    setSortBy((s) => (s === "default" ? "salary" : s === "salary" ? "match" : "default"));

  const handleSearch = () => {
    onSearch?.({
      source: activeSource,
      query: query || "data engineer",
      remote_only: remoteOnly,
      experience_level: experienceLevel,
      employment_type: employmentType,
    });
  };

  const handleSourceChange = (src: JobSource) => {
    onSourceChange?.(src);
    onSearch?.({ source: src, query: query || "data engineer" });
  };

  const filtered = jobs
    .filter((j) => {
      if (!query) return true;
      const q = query.toLowerCase();
      return (
        j.title.toLowerCase().includes(q) ||
        j.company.toLowerCase().includes(q) ||
        j.description.toLowerCase().includes(q) ||
        j.skills.some((s) => s.toLowerCase().includes(q))
      );
    })
    .sort((a, b) => {
      if (sortBy === "salary") return (b.salary_max ?? 0) - (a.salary_max ?? 0);
      if (sortBy === "match") {
        const sa = matchScores[a.source_job_id] ?? 0;
        const sb = matchScores[b.source_job_id] ?? 0;
        return sb - sa;
      }
      return 0;
    });

  const activeFiltersCount = [remoteOnly, !!experienceLevel, !!employmentType].filter(Boolean).length;

  return (
    <div className="panel job-panel">
      {/* Toolbar */}
      <div className="toolbar">
        {/* Source selector */}
        <div className="source-selector">
          {(Object.keys(SOURCE_LABELS) as JobSource[]).map((src) => (
            <button
              key={src}
              className={`source-tab ${activeSource === src ? "active" : ""}`}
              onClick={() => handleSourceChange(src)}
              disabled={loading}
            >
              {SOURCE_LABELS[src]}
            </button>
          ))}
        </div>

        <label className="search-label">
          <Search size={16} className="search-icon" />
          <input
            className="search-input"
            placeholder="Search title, company, or skill…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            aria-label="Search jobs"
          />
          {query && (
            <button
              className="search-clear"
              onClick={() => setQuery("")}
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </label>

        <button
          className={`icon-btn ${showFilters ? "active" : ""}`}
          title="Filters"
          aria-label="Toggle filters"
          onClick={() => setShowFilters((v) => !v)}
        >
          <Filter size={16} />
          {activeFiltersCount > 0 && (
            <span className="filter-badge">{activeFiltersCount}</span>
          )}
        </button>

        <button
          className="icon-btn"
          title={`Sort: ${sortBy}`}
          aria-label="Toggle sort"
          onClick={cycleSort}
        >
          <ArrowUpDown size={16} />
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="filter-panel">
          <div className="filter-row">
            <label className="filter-field">
              <span className="filter-label">Experience</span>
              <select
                className="select select-sm"
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value as typeof experienceLevel)}
              >
                <option value="">Any level</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid-level</option>
                <option value="senior">Senior</option>
              </select>
            </label>

            <label className="filter-field">
              <span className="filter-label">Type</span>
              <select
                className="select select-sm"
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value as typeof employmentType)}
              >
                <option value="">Any type</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="freelance">Freelance</option>
              </select>
            </label>

            <label className="filter-toggle">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={(e) => setRemoteOnly(e.target.checked)}
              />
              <span>Remote only</span>
            </label>

            <button className="primary-sm" onClick={handleSearch} disabled={loading}>
              {loading ? "Searching…" : "Apply & Search"}
            </button>
          </div>
        </div>
      )}

      <div className="panel-header">
        <h2>Job Explorer</h2>
        <span>
          {loading ? (
            <span className="loading-dots">Fetching live jobs…</span>
          ) : (
            `${filtered.length} roles from ${SOURCE_LABELS[activeSource]}`
          )}
        </span>
      </div>

      <div className="job-list">
        {loading ? (
          <div className="skeleton-stack">
            <div className="skeleton" />
            <div className="skeleton" />
            <div className="skeleton short" />
          </div>
        ) : filtered.length === 0 ? (
          <p className="empty-state">
            No jobs found.{" "}
            <button className="link-btn" onClick={handleSearch}>
              Try a broader search
            </button>
          </p>
        ) : (
          filtered.map((job) => (
            <JobCard
              key={job.source_job_id}
              job={job}
              matchScore={matchScores[job.source_job_id]}
              saved={saved.has(job.source_job_id)}
              onSave={() => toggleSave(job.source_job_id)}
              onClick={() => setSelected(job === selected ? null : job)}
            />
          ))
        )}
      </div>

      {/* Detail drawer */}
      {selected && (
        <div className="job-detail-overlay" onClick={() => setSelected(null)}>
          <div className="job-detail" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelected(null)} aria-label="Close">
              ✕
            </button>
            <div className="job-detail-source">{SOURCE_LABELS[selected.source as JobSource] ?? selected.source}</div>
            <h2>{selected.title}</h2>
            <p className="job-detail-company">{selected.company}</p>
            <p className="job-detail-location">{selected.location}</p>
            <p className="job-detail-salary">{formatSalary(selected)}</p>
            <div className="skill-row" style={{ marginBottom: 16 }}>
              {selected.skills.map((s) => (
                <span key={s} className="skill-chip">
                  {s}
                </span>
              ))}
            </div>
            <p className="job-detail-desc">{selected.description}</p>
            {selected.url && (
              <a className="apply-link" href={selected.url} target="_blank" rel="noreferrer">
                Apply ↗
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
