"use client";

import type { MetricItem } from "../lib/types";

interface MetricCardProps extends MetricItem {}

function MetricCard({ label, value, trend, positive = true }: MetricCardProps) {
  return (
    <div className="metric">
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      <small className={`metric-trend ${positive ? "positive" : "negative"}`}>{trend}</small>
    </div>
  );
}

interface MetricsBarProps {
  items: MetricItem[];
}

export default function MetricsBar({ items }: MetricsBarProps) {
  return (
    <section className="metrics" aria-label="Platform metrics">
      {items.map((item) => (
        <MetricCard key={item.label} {...item} />
      ))}
    </section>
  );
}
