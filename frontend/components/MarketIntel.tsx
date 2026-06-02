"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalyticsResponse } from "../lib/types";

interface MarketIntelProps {
  data: AnalyticsResponse;
}

const TEAL = "#0d9488";
const AMBER = "#f59e0b";
const GRADIENT_COLORS = ["#0d9488", "#0f766e", "#115e59", "#134e4a", "#0c3a36"];

export default function MarketIntel({ data }: MarketIntelProps) {
  const skillData = data.top_skills.map((item) => ({
    skill: (item.skill as string) ?? "Unknown",
    jobs: (item.count as number) ?? 0,
  }));

  const trendData = data.market_trends.map((item) => ({
    period: (item.period as string) ?? "",
    jobs: (item.jobs as number) ?? 0,
  }));

  const payingData = data.top_paying_skills.map((item) => ({
    skill: (item.skill as string) ?? "Unknown",
    avg: Math.round(((item.avg as number) ?? 0) / 1000),
  }));

  return (
    <div className="panel market-panel">
      <div className="panel-header">
        <h2>Market Intelligence</h2>
        <span>Real-time demand</span>
      </div>

      <div className="chart-grid">
        {/* Top Skills Bar Chart */}
        <div className="chart-block">
          <h3 className="chart-title">Top Skills in Demand</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={skillData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e2d3d" />
              <XAxis dataKey="skill" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #1e2d3d", borderRadius: 8 }}
                labelStyle={{ color: "#e2e8f0" }}
                itemStyle={{ color: TEAL }}
              />
              <Bar dataKey="jobs" radius={[4, 4, 0, 0]}>
                {skillData.map((_, i) => (
                  <Cell key={i} fill={GRADIENT_COLORS[i % GRADIENT_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Market Trend Line Chart */}
        <div className="chart-block">
          <h3 className="chart-title">Hiring Trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e2d3d" />
              <XAxis dataKey="period" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #1e2d3d", borderRadius: 8 }}
                labelStyle={{ color: "#e2e8f0" }}
                itemStyle={{ color: TEAL }}
              />
              <Line
                type="monotone"
                dataKey="jobs"
                stroke={TEAL}
                strokeWidth={2.5}
                dot={{ fill: TEAL, r: 4 }}
                activeDot={{ r: 6, fill: AMBER }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Paying Skills */}
        <div className="chart-block full-col">
          <h3 className="chart-title">Top Paying Skills (avg $k)</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart
              data={payingData}
              layout="vertical"
              margin={{ top: 4, right: 8, left: 60, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#1e2d3d" />
              <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="skill" type="category" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #1e2d3d", borderRadius: 8 }}
                labelStyle={{ color: "#e2e8f0" }}
                itemStyle={{ color: AMBER }}
                formatter={(val: number) => [`$${val}k`, "Avg salary"]}
              />
              <Bar dataKey="avg" radius={[0, 4, 4, 0]} fill={AMBER} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
