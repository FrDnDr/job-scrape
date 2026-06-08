"use client";

import { Upload, X } from "lucide-react";
import { useRef, useState } from "react";
import { matchResumeToJob, uploadResumePdf, parseResumeText } from "../lib/api";
import type { MatchResponse, ResumeProfile, WarehouseJobPosting } from "../lib/types";

interface ResumeMatchProps {
  jobs: WarehouseJobPosting[];
  onProfileLoaded?: (profile: ResumeProfile) => void;
  onMatchResult?: (match: MatchResponse) => void;
}

export default function ResumeMatch({ jobs, onProfileLoaded, onMatchResult }: ResumeMatchProps) {
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [match, setMatch] = useState<MatchResponse | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<string>(jobs[0]?.source_job_id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [tab, setTab] = useState<"upload" | "paste">("upload");
  const fileRef = useRef<HTMLInputElement>(null);

  const selectedJob = jobs.find((j) => j.source_job_id === selectedJobId) ?? jobs[0];

  const handleMatchResult = (m: MatchResponse) => {
    setMatch(m);
    onMatchResult?.(m);
  };

  const handleFile = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const parsed = await uploadResumePdf(file);
      setProfile(parsed);
      onProfileLoaded?.(parsed);
      if (selectedJob) {
        const m = await matchResumeToJob(parsed.resume_text, selectedJob);
        handleMatchResult(m);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handlePaste = async () => {
    if (!resumeText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const parsed = await parseResumeText(resumeText);
      setProfile(parsed);
      onProfileLoaded?.(parsed);
      if (selectedJob) {
        const m = await matchResumeToJob(resumeText, selectedJob);
        handleMatchResult(m);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (s: number) =>
    s >= 80 ? "var(--teal)" : s >= 60 ? "var(--amber)" : "var(--red)";

  return (
    <div className="panel resume-panel">
      <div className="panel-header">
        <h2>Resume Match</h2>
        <span>AI-powered scoring</span>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)} aria-label="Dismiss error">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Job selector */}
      {jobs.length > 0 && (
        <label className="field-label">
          Match against job
          <select
            className="select"
            value={selectedJobId}
            onChange={(e) => {
              setSelectedJobId(e.target.value);
              setMatch(null);
            }}
          >
            {jobs.map((j) => (
              <option key={j.source_job_id} value={j.source_job_id}>
                {j.title} @ {j.company}
              </option>
            ))}
          </select>
        </label>
      )}

      {/* Tab switcher */}
      <div className="tab-bar">
        <button
          className={tab === "upload" ? "tab active" : "tab"}
          onClick={() => setTab("upload")}
        >
          Upload PDF
        </button>
        <button
          className={tab === "paste" ? "tab active" : "tab"}
          onClick={() => setTab("paste")}
        >
          Paste Text
        </button>
      </div>

      {tab === "upload" ? (
        <div
          className="drop-zone"
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f) handleFile(f);
          }}
          tabIndex={0}
          role="button"
          aria-label="Upload resume PDF"
          onKeyDown={(e) => e.key === "Enter" && fileRef.current?.click()}
        >
          <Upload size={28} />
          <span>Drop PDF here or click to browse</span>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt"
            hidden
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <div className="paste-zone">
          <textarea
            className="resume-textarea"
            placeholder="Paste your resume text here…"
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={6}
          />
          <button
            className="primary full-width"
            onClick={handlePaste}
            disabled={loading || !resumeText.trim()}
          >
            {loading ? "Analysing…" : "Analyse Resume"}
          </button>
        </div>
      )}

      {loading && (
        <div className="skeleton-stack">
          <div className="skeleton" />
          <div className="skeleton" />
          <div className="skeleton short" />
        </div>
      )}

      {match && !loading && (
        <div className="match-results">
          {/* Score ring */}
          <div
            className="score-ring"
            style={{
              background: `conic-gradient(${scoreColor(match.match_score)} ${match.match_score * 3.6}deg, #1e2d3d 0deg)`,
            }}
          >
            <div className="score-ring-inner">
              <span className="score-num">{match.match_score}</span>
              <small>/ 100</small>
            </div>
          </div>

          {/* Overlap badge */}
          {match.skill_overlap > 0 && (
            <div className="overlap-badge">
              <span className="overlap-label">Skill overlap</span>
              <span className="overlap-value">{match.skill_overlap.toFixed(0)}%</span>
            </div>
          )}

          <div className="match-grid">
            <div className="match-section strengths">
              <h3>Strengths ({match.strengths.length})</h3>
              <ul>
                {match.strengths.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
            <div className="match-section gaps">
              <h3>Skill Gaps ({match.missing_skills.length})</h3>
              <ul>
                {match.missing_skills.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="recommendation">
            <h3>AI Recommendation</h3>
            <p>{match.recommendation}</p>
          </div>
        </div>
      )}

      {profile && !match && !loading && (
        <div className="profile-preview">
          <h3>{profile.candidate_name ?? "Candidate"}</h3>
          {profile.education_level && (
            <p className="edu-badge">{profile.education_level}</p>
          )}
          {profile.years_experience != null && (
            <p>{profile.years_experience} years experience</p>
          )}
          <div className="skill-row">
            {profile.skills.map((s) => (
              <span key={s} className="skill-chip">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
