"use client";

import type { RoadmapItem } from "../lib/types";

interface LearningRoadmapProps {
  items: RoadmapItem[];
  missingSkills?: string[];
}

// Effort estimates for known skills (fallback when backend data not available)
const EFFORT_MAP: Record<string, string> = {
  airflow: "3 weeks",
  aws: "4 weeks",
  azure: "4 weeks",
  bigquery: "2 weeks",
  "ci/cd": "2 weeks",
  dbt: "2 weeks",
  docker: "2 weeks",
  elasticsearch: "2 weeks",
  fastapi: "1 week",
  gcp: "4 weeks",
  graphql: "1 week",
  javascript: "4 weeks",
  kafka: "3 weeks",
  kubernetes: "5 weeks",
  langchain: "2 weeks",
  llm: "3 weeks",
  "machine learning": "6 weeks",
  "next.js": "2 weeks",
  postgresql: "2 weeks",
  python: "4 weeks",
  react: "3 weeks",
  redis: "1 week",
  snowflake: "2 weeks",
  spark: "4 weeks",
  sql: "3 weeks",
  terraform: "3 weeks",
  typescript: "2 weeks",
};

function priorityFromIndex(i: number): "High" | "Medium" | "Low" {
  if (i < 2) return "High";
  if (i < 5) return "Medium";
  return "Low";
}

function buildRoadmapFromMissing(missingSkills: string[]): RoadmapItem[] {
  return missingSkills.slice(0, 8).map((skill, i) => ({
    skill,
    priority: priorityFromIndex(i),
    effort: EFFORT_MAP[skill.toLowerCase()] ?? "2 weeks",
  }));
}

const PRIORITY_COLORS: Record<string, string> = {
  High: "var(--red)",
  Medium: "var(--amber)",
  Low: "var(--teal)",
};

const PRIORITY_BG: Record<string, string> = {
  High: "rgba(244,63,94,0.12)",
  Medium: "rgba(245,158,11,0.12)",
  Low: "rgba(13,148,136,0.12)",
};

export default function LearningRoadmap({ items, missingSkills }: LearningRoadmapProps) {
  // If missingSkills provided (from resume match), build dynamic roadmap
  const displayItems: RoadmapItem[] =
    missingSkills && missingSkills.length > 0
      ? buildRoadmapFromMissing(missingSkills)
      : items;

  const hasDynamicData = missingSkills && missingSkills.length > 0;

  return (
    <div className="panel roadmap-panel">
      <div className="panel-header">
        <h2>Learning Roadmap</h2>
        <span>{hasDynamicData ? "Based on your skill gaps" : "Suggested path"}</span>
      </div>

      {displayItems.length === 0 ? (
        <div className="roadmap-empty">
          <p>Upload your resume and run a match to get a personalized learning roadmap.</p>
        </div>
      ) : (
        <ol className="roadmap-list">
          {displayItems.map((item, i) => (
            <li key={item.skill} className="roadmap-item">
              <span className="roadmap-step">{i + 1}</span>
              <div className="roadmap-content">
                <div className="roadmap-skill-row">
                  <span className="roadmap-skill">{item.skill}</span>
                  <span
                    className="roadmap-priority"
                    style={{
                      color: PRIORITY_COLORS[item.priority],
                      background: PRIORITY_BG[item.priority],
                    }}
                  >
                    {item.priority}
                  </span>
                </div>
                <span className="roadmap-effort">⏱ {item.effort}</span>
                {item.resources && item.resources.length > 0 && (
                  <div className="roadmap-resources">
                    {item.resources.map((r) => (
                      <a key={r} href={r} target="_blank" rel="noreferrer" className="resource-link">
                        {r}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
