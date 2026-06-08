"use client";

import { Bookmark, BookmarkCheck } from "lucide-react";
import type { WarehouseJobPosting } from "../lib/types";

export function formatSalary(job: WarehouseJobPosting): string {
  if (job.salary_min == null && job.salary_max == null) return "Salary undisclosed";
  const cur = job.salary_currency ?? "USD";
  const fmt = (n: number) =>
    cur === "USD" || cur === "PHP"
      ? `${cur === "PHP" ? "₱" : "$"}${Math.round(n / 1000)}k`
      : `${cur} ${Math.round(n / 1000)}k`;
  if (job.salary_min != null && job.salary_max != null) return `${fmt(job.salary_min)} – ${fmt(job.salary_max)}`;
  if (job.salary_min != null) return `From ${fmt(job.salary_min)}`;
  return `Up to ${fmt(job.salary_max!)}`;
}

export function descriptionExcerpt(description: string, maxLength = 180): string {
  const normalized = description.replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, maxLength).trimEnd()}...`;
}

export interface JobCardProps {
  job: WarehouseJobPosting;
  matchScore?: number;
  saved: boolean;
  onSave: () => void;
  onClick: () => void;
}

export default function JobCard({ job, matchScore, saved, onSave, onClick }: JobCardProps) {
  return (
    <article
      className="job-card"
      onClick={onClick}
      tabIndex={0}
      role="button"
      onKeyDown={(e) => e.key === "Enter" && onClick()}
    >
      <div className="job-main">
        <div className="job-info">
          <h3>{job.title}</h3>
          <p className="job-card-salary">{formatSalary(job)}</p>
        </div>
        <button
          className={`save-btn ${saved ? "saved" : ""}`}
          title={saved ? "Unsave job" : "Save job"}
          aria-label={`${saved ? "Unsave" : "Save"} ${job.title}`}
          onClick={(e) => {
            e.stopPropagation();
            onSave();
          }}
        >
          {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
        </button>
      </div>

      <p className="job-card-description">
        {descriptionExcerpt(job.description || "No description available.")}
      </p>

      <div className="job-meta">
        <span>{job.company}</span>
        <span>{job.location ?? "Location not specified"}</span>
        {matchScore !== undefined && (
          <strong className="match-badge">{matchScore}% match</strong>
        )}
      </div>

      <div className="skill-row">
        {job.skills.slice(0, 6).map((skill) => (
          <span key={skill} className="skill-chip">{skill}</span>
        ))}
        {job.skills.length > 6 && (
          <span className="skill-chip muted">+{job.skills.length - 6}</span>
        )}
      </div>
    </article>
  );
}
