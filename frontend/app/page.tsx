"use client";

import { useState } from "react";
import {
  JobExplorer,
  LearningRoadmap,
  MarketIntel,
  MetricsBar,
  ResumeMatch,
  Sidebar,
  TopBar,
} from "../components";
import { useDashboard } from "../lib/hooks/useDashboard";
import type { NavSection } from "../lib/types";

export default function Dashboard() {
  const [activeSection, setActiveSection] = useState<NavSection>("jobs");
  const [bannerDismissed, setBannerDismissed] = useState(false);

  const {
    jobs,
    analytics,
    loading,
    error,
    usingDemoData,
    metrics,
    matchResult,
    activeSource,
    setProfile,
    setMatchResult,
    setActiveSource,
    loadData,
  } = useDashboard();

  const scrollToSection = (section: NavSection) => {
    setActiveSection(section);
    document.getElementById(section)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="shell">
      <Sidebar active={activeSection} onNavigate={scrollToSection} />

      <section className="workspace">
        <TopBar
          onUploadResume={() => scrollToSection("match")}
          onRefresh={() => loadData({ source: activeSource })}
          loading={loading}
        />

        {/* Demo-data notice */}
        {usingDemoData && !bannerDismissed && (
          <div className="demo-banner" role="alert">
            <span>
              ⚠️ <strong>Demo data</strong> — backend offline.{" "}
              {error && <em style={{ opacity: 0.75 }}>{error}</em>}
            </span>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                className="banner-btn"
                onClick={() => loadData({ source: activeSource })}
                disabled={loading}
              >
                Retry
              </button>
              <button
                className="banner-btn secondary"
                onClick={() => setBannerDismissed(true)}
                aria-label="Dismiss banner"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        <MetricsBar items={metrics} />

        <div className="content-grid">
          {/* ── Left column: full-height job explorer ── */}
          <div className="col-main" id="jobs">
            <JobExplorer
              jobs={jobs}
              activeSource={activeSource}
              loading={loading}
              onSourceChange={(src) => {
                setActiveSource(src);
                loadData({ source: src });
              }}
              onSearch={(opts) => loadData(opts)}
            />
          </div>

          {/* ── Right column: stacked panels ── */}
          <div className="col-side">
            <div id="match">
              <ResumeMatch
                jobs={jobs}
                onProfileLoaded={setProfile}
                onMatchResult={setMatchResult}
              />
            </div>
            <div id="market">
              <MarketIntel data={analytics} />
            </div>
            <div id="roadmap">
              <LearningRoadmap
                items={[]}
                missingSkills={matchResult?.missing_skills}
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
