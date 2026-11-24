"use client";

import React, { useState } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, DollarSign } from "lucide-react";

interface Props {
  className?: string;
}

const DEFAULT_CTC_DATA = [
  { bracket: "3-6 LPA", count: 480, label: "Core/Foundation", cumulative: 480 },
  { bracket: "6-10 LPA", count: 850, label: "Mid-Tier Tech", cumulative: 1330 },
  { bracket: "10-15 LPA", count: 420, label: "High Growth", cumulative: 1750 },
  { bracket: "15-25 LPA", count: 285, label: "Tier-1 Product", cumulative: 2035 },
  { bracket: "25-35 LPA", count: 110, label: "Dream Package", cumulative: 2145 },
  { bracket: "35-50 LPA", count: 40, label: "Super Dream", cumulative: 2185 },
];

export function CTCDistributionChart({ className = "" }: Props) {
  const [chartType, setChartType] = useState<"area" | "bar">("area");

  return (
    <div
      className={`rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm ${className}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <DollarSign className="h-4 w-4" />
            </div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base">
              CTC Package Distribution (LPA Bands)
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Offers across compensation tiers and density curve
          </p>
        </div>

        {/* Chart type toggle */}
        <div className="flex items-center rounded-xl bg-slate-100 dark:bg-slate-800 p-1 self-start sm:self-auto">
          <button
            onClick={() => setChartType("area")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              chartType === "area"
                ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            Density Curve
          </button>
          <button
            onClick={() => setChartType("bar")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              chartType === "bar"
                ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            Tier Columns
          </button>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "area" ? (
            <AreaChart
              data={DEFAULT_CTC_DATA}
              margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
            >
              <defs>
                <linearGradient id="ctcGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e2e8f0"
                className="dark:stroke-slate-800"
              />
              <XAxis
                dataKey="bracket"
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
                        <p className="font-bold text-slate-900 dark:text-white text-xs">
                          {data.bracket} ({data.label})
                        </p>
                        <p className="text-emerald-600 dark:text-emerald-400 font-bold text-sm mt-1">
                          {data.count} Placements
                        </p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                          Cumulative: {data.cumulative} students
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                name="Placed Students"
                stroke="#10b981"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#ctcGradient)"
              />
            </AreaChart>
          ) : (
            <BarChart
              data={DEFAULT_CTC_DATA}
              margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e2e8f0"
                className="dark:stroke-slate-800"
              />
              <XAxis
                dataKey="bracket"
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
                        <p className="font-bold text-slate-900 dark:text-white text-xs">
                          {data.bracket} ({data.label})
                        </p>
                        <p className="text-emerald-600 dark:text-emerald-400 font-bold text-sm mt-1">
                          {data.count} Candidates
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar
                dataKey="count"
                fill="#10b981"
                radius={[6, 6, 0, 0]}
                barSize={32}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default CTCDistributionChart;
