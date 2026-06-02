"use client";

import { BriefcaseBusiness, ChartNoAxesColumnIncreasing, CircleGauge, Sparkles } from "lucide-react";
import type { NavSection } from "../lib/types";

const NAV_ITEMS: { id: NavSection; label: string; Icon: React.ElementType }[] = [
  { id: "jobs", label: "Jobs", Icon: BriefcaseBusiness },
  { id: "match", label: "Match", Icon: CircleGauge },
  { id: "market", label: "Market", Icon: ChartNoAxesColumnIncreasing },
  { id: "roadmap", label: "Roadmap", Icon: Sparkles },
];

interface SidebarProps {
  active: NavSection;
  onNavigate: (section: NavSection) => void;
}

export default function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand">
        <div className="brand-mark">JI</div>
        <div>
          <strong>Job Intelligence</strong>
          <span>Data platform</span>
        </div>
      </div>

      <nav className="nav">
        {NAV_ITEMS.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`nav-btn${active === id ? " active" : ""}`}
            onClick={() => onNavigate(id)}
            aria-current={active === id ? "page" : undefined}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot" />
        <span>Backend connected</span>
      </div>
    </aside>
  );
}
