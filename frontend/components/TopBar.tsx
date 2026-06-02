"use client";

import { FileText, RefreshCw } from "lucide-react";

interface TopBarProps {
  onUploadResume: () => void;
  onRefresh: () => void;
  loading?: boolean;
}

export default function TopBar({ onUploadResume, onRefresh, loading }: TopBarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Portfolio MVP</p>
        <h1>AI-Powered Job Intelligence</h1>
      </div>
      <div className="topbar-actions">
        <button
          className="icon-btn"
          onClick={onRefresh}
          title="Refresh data from backend"
          aria-label="Refresh data"
          disabled={loading}
        >
          <RefreshCw size={18} className={loading ? "spin" : ""} />
        </button>
        <button className="primary" onClick={onUploadResume} id="upload-resume-btn">
          <FileText size={18} />
          Upload Resume
        </button>
      </div>
    </header>
  );
}
