"use client";

import React from "react";
import { Users, Award, TrendingUp, DollarSign, ArrowUpRight } from "lucide-react";
import { LiveKPIData } from "@/lib/types";
import { formatCurrencyLPA, formatPercentage } from "@/lib/utils";

interface Props {
  kpi: LiveKPIData;
  className?: string;
}

export function PlacementOverviewCards({ kpi, className = "" }: Props) {
  const cards = [
    {
      label: "Total Registered Candidates",
      value: kpi.total_students.toLocaleString(),
      subtext: `${kpi.total_offers.toLocaleString()} total offers rolled out`,
      change: "+12.4% vs last season",
      isPositive: true,
      icon: Users,
      accent: "from-blue-500/10 to-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-900/50",
      iconBg: "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400",
      progress: Math.min(100, (kpi.placed_students / kpi.total_students) * 100),
    },
    {
      label: "Placement Conversion Rate",
      value: formatPercentage(kpi.placement_percentage),
      subtext: `${kpi.placed_students.toLocaleString()} students placed`,
      change: "+8.2% vs national benchmark",
      isPositive: true,
      icon: Award,
      accent: "from-emerald-500/10 to-teal-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50",
      iconBg: "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400",
      progress: kpi.placement_percentage,
    },
    {
      label: "Average CTC Package",
      value: formatCurrencyLPA(kpi.average_ctc_lpa),
      subtext: `Median CTC: ${formatCurrencyLPA(kpi.median_ctc_lpa)}`,
      change: "+15.6% salary uplift",
      isPositive: true,
      icon: TrendingUp,
      accent: "from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-900/50",
      iconBg: "bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400",
      progress: 68,
    },
    {
      label: "Highest Campus Offer",
      value: formatCurrencyLPA(kpi.highest_ctc_lpa),
      subtext: kpi.recent_offer
        ? `Latest: ${kpi.recent_offer.company} (${formatCurrencyLPA(kpi.recent_offer.ctc_lpa)})`
        : "Record package by DE Shaw & Co",
      change: "All-time institutional high",
      isPositive: true,
      icon: DollarSign,
      accent: "from-purple-500/10 to-pink-500/10 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-900/50",
      iconBg: "bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400",
      progress: 95,
    },
  ];

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="group relative overflow-hidden rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm hover:shadow-md transition-all duration-300"
          >
            <div className="flex items-start justify-between">
              <span className="text-xs font-semibold tracking-wider uppercase text-slate-500 dark:text-slate-400">
                {card.label}
              </span>
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-xl transition-transform group-hover:scale-110 ${card.iconBg}`}
              >
                <Icon className="h-5 w-5" />
              </div>
            </div>

            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {card.value}
              </span>
            </div>

            <div className="mt-2 flex items-center justify-between text-xs">
              <span className="text-slate-600 dark:text-slate-400 font-medium truncate max-w-[180px]">
                {card.subtext}
              </span>
              <span className="inline-flex items-center gap-0.5 text-emerald-600 dark:text-emerald-400 font-semibold text-[11px] bg-emerald-50 dark:bg-emerald-950/50 px-1.5 py-0.5 rounded-md">
                <ArrowUpRight className="h-3 w-3" />
                {card.change}
              </span>
            </div>

            {/* Micro progress indicator */}
            <div className="mt-3.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="h-full rounded-full bg-indigo-600 dark:bg-indigo-500 transition-all duration-700 ease-out"
                style={{ width: `${Math.min(100, Math.max(5, card.progress))}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
export default PlacementOverviewCards;
