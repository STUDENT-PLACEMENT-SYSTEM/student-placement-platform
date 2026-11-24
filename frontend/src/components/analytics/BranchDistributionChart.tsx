"use client";

import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { BarChart3, PieChart as PieIcon, Layers } from "lucide-react";

interface Props {
  branchData?: Record<
    string,
    { placed: number; total: number; percent: number }
  >;
  className?: string;
}

const COLORS = [
  "#6366f1", // Indigo
  "#06b6d4", // Cyan
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#ec4899", // Pink
  "#8b5cf6", // Purple
  "#64748b", // Slate
];

export function BranchDistributionChart({
  branchData = {
    "Computer Science": { placed: 630, total: 650, percent: 96.9 },
    "Information Technology": { placed: 420, total: 450, percent: 93.3 },
    ECE: { placed: 440, total: 520, percent: 84.6 },
    Mechanical: { placed: 295, total: 450, percent: 65.5 },
    Civil: { placed: 210, total: 430, percent: 48.8 },
    Chemical: { placed: 190, total: 500, percent: 38.0 },
  },
  className = "",
}: Props) {
  const [viewMode, setViewMode] = useState<"bar" | "pie">("bar");

  // Format data for Recharts
  const chartData = Object.entries(branchData).map(([branch, stats]) => ({
    name: branch.replace("Computer Science", "CSE").replace("Information Technology", "IT"),
    fullName: branch,
    placed: stats.placed,
    unplaced: Math.max(0, stats.total - stats.placed),
    total: stats.total,
    placementRate: stats.percent,
  }));

  return (
    <div
      className={`rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm ${className}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <Layers className="h-4 w-4" />
            </div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base">
              Branch-wise Placement Statistics
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Departmental placement performance and recruitment distribution
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center rounded-xl bg-slate-100 dark:bg-slate-800 p-1 self-start sm:self-auto">
          <button
            onClick={() => setViewMode("bar")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === "bar"
                ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" />
            Bar Chart
          </button>
          <button
            onClick={() => setViewMode("pie")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === "pie"
                ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <PieIcon className="h-3.5 w-3.5" />
            Share (Donut)
          </button>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {viewMode === "bar" ? (
            <BarChart
              data={chartData}
              margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e2e8f0"
                className="dark:stroke-slate-800"
              />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-3 shadow-lg">
                        <p className="font-bold text-slate-900 dark:text-white text-xs mb-1">
                          {data.fullName}
                        </p>
                        <div className="space-y-1 text-xs">
                          <p className="text-indigo-600 dark:text-indigo-400 font-medium">
                            Placed: {data.placed} students ({data.placementRate}%)
                          </p>
                          <p className="text-slate-500 dark:text-slate-400">
                            Unplaced: {data.unplaced} students
                          </p>
                          <p className="text-slate-700 dark:text-slate-300 font-semibold border-t border-slate-100 dark:border-slate-700 pt-1 mt-1">
                            Total Batch: {data.total}
                          </p>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                verticalAlign="top"
                align="right"
                wrapperStyle={{ paddingBottom: 12, fontSize: 12 }}
              />
              <Bar
                name="Placed Students"
                dataKey="placed"
                fill="#6366f1"
                radius={[6, 6, 0, 0]}
                barSize={24}
              />
              <Bar
                name="Unplaced Candidates"
                dataKey="unplaced"
                fill="#cbd5e1"
                radius={[6, 6, 0, 0]}
                barSize={24}
              />
            </BarChart>
          ) : (
            <PieChart>
              <Pie
                data={chartData}
                dataKey="placed"
                nameKey="fullName"
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={4}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-3 shadow-lg">
                        <p className="font-bold text-slate-900 dark:text-white text-xs mb-1">
                          {data.fullName}
                        </p>
                        <p className="text-indigo-600 dark:text-indigo-400 font-semibold text-xs">
                          Placed: {data.placed} ({data.placementRate}%)
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                wrapperStyle={{ fontSize: 11 }}
              />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default BranchDistributionChart;
