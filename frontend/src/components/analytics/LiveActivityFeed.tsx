"use client";

import React from "react";
import {
  Radio,
  Briefcase,
  Sparkles,
  CheckCircle2,
  Calendar,
  Building,
} from "lucide-react";
import { LivePlacementEvent } from "@/lib/types";
import { formatCurrencyLPA } from "@/lib/utils";

interface Props {
  events: LivePlacementEvent[];
  isConnected?: boolean;
  isSimulated?: boolean;
  className?: string;
}

export function LiveActivityFeed({
  events,
  isConnected = true,
  isSimulated = false,
  className = "",
}: Props) {
  const getEventIcon = (type: LivePlacementEvent["type"]) => {
    switch (type) {
      case "offer":
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      case "drive_announced":
        return <Calendar className="h-4 w-4 text-indigo-500" />;
      case "shortlisted":
        return <Sparkles className="h-4 w-4 text-amber-500" />;
      default:
        return <Briefcase className="h-4 w-4 text-slate-500" />;
    }
  };

  const formatTimeAgo = (isoString: string) => {
    const diffMs = Date.now() - new Date(isoString).getTime();
    const diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 45) return "Just now";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    return `${diffHr}h ago`;
  };

  return (
    <div
      className={`rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm flex flex-col ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="relative flex h-3 w-3">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isConnected ? "bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-3 w-3 ${
                isConnected ? "bg-emerald-500" : "bg-rose-500"
              }`}
            />
          </div>
          <h3 className="font-bold text-slate-900 dark:text-white text-base">
            Live Placement Stream
          </h3>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 px-2.5 py-1 rounded-full">
          <Radio className="h-3 w-3 text-emerald-500 animate-pulse" />
          <span>{isSimulated ? "SSE Emulated" : "SSE Live Feed"}</span>
        </div>
      </div>

      {/* Events List */}
      <div className="mt-4 space-y-3 overflow-y-auto max-h-[380px] pr-1 divide-y divide-slate-100/80 dark:divide-slate-800/60">
        {events.length === 0 ? (
          <p className="text-center text-xs text-slate-400 py-8">
            Waiting for real-time placement events...
          </p>
        ) : (
          events.map((ev) => (
            <div
              key={ev.id}
              className="pt-3 first:pt-0 flex items-start gap-3 transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/30 p-2 rounded-xl"
            >
              <div className="mt-0.5 p-2 rounded-xl bg-slate-100 dark:bg-slate-800 shrink-0">
                {getEventIcon(ev.type)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1">
                  <p className="text-xs font-bold text-slate-900 dark:text-white truncate">
                    {ev.student_name}
                  </p>
                  <span className="text-[10px] text-slate-600 dark:text-slate-400 font-medium shrink-0">
                    {formatTimeAgo(ev.timestamp)}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-600 dark:text-slate-300">
                  <Building className="h-3 w-3 text-slate-600 shrink-0" />
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                    {ev.company}
                  </span>
                  {ev.branch && (
                    <span className="text-[10px] text-slate-600 dark:text-slate-400">
                      • {ev.branch}
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">
                  {ev.message}
                </p>
              </div>

              {ev.ctc_lpa && (
                <div className="shrink-0 self-center">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-900/60">
                    {formatCurrencyLPA(ev.ctc_lpa)}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
export default LiveActivityFeed;
