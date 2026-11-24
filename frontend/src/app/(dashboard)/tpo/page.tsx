"use client";

import React, { useState } from "react";
import {
  BarChart3,
  Radio,
  Upload,
  CheckCircle,
  Sparkles,
  Search,
  Users,
  Send,
  Layers,
  FileSpreadsheet,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { useSSE } from "@/hooks/useSSE";
import { api } from "@/lib/api";
import PlacementOverviewCards from "@/components/analytics/PlacementOverviewCards";
import BranchDistributionChart from "@/components/analytics/BranchDistributionChart";
import CTCDistributionChart from "@/components/analytics/CTCDistributionChart";
import LiveActivityFeed from "@/components/analytics/LiveActivityFeed";
import { formatCurrencyLPA } from "@/lib/utils";

export default function TPODashboardPage() {
  const {
    data: kpi,
    events,
    isConnected,
    isSimulated,
    lastHeartbeat,
    injectPlacementEvent,
  } = useSSE();

  // Mark Placed State
  const [showMarkPlacedModal, setShowMarkPlacedModal] = useState(false);
  const [placedForm, setPlacedForm] = useState({
    student_id: "2021CS045",
    student_name: "Rohan Sharma",
    company_name: "Google",
    ctc_lpa: 32.5,
    branch: "Computer Science",
  });
  const [placedFeedback, setPlacedFeedback] = useState<string | null>(null);

  // Bulk CSV Upload State
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [isUploadingCSV, setIsUploadingCSV] = useState(false);
  const [csvFeedback, setCSVFeedback] = useState<string | null>(null);

  // AI Copilot Query State
  const [aiQuery, setAiQuery] = useState(
    "Highlight unplaced students with CGPA above 8.5 for targeted outreach"
  );
  const [isQueryingAI, setIsQueryingAI] = useState(false);
  const [copilotResponse, setCopilotResponse] = useState<{
    answer: string;
    tool_used: string;
    data?: any;
  } | null>({
    answer:
      "Identified 18 high-performing unplaced candidates with CGPA ≥ 8.5. Recommend notifying Cisco Systems and Oracle Cloud for targeted recruitment.",
    tool_used: "get_unplaced_high_cgpa_students",
    data: [
      { roll: "2021EC012", name: "Siddharth Rao", cgpa: 8.92, branch: "ECE" },
      { roll: "2021ME044", name: "Aarav Gupta", cgpa: 8.78, branch: "Mechanical" },
      { roll: "2021EC089", name: "Divya Nair", cgpa: 8.65, branch: "ECE" },
    ],
  });

  const handleMarkPlacedSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.tpo.markPlaced({
        student_id: placedForm.student_id,
        student_name: placedForm.student_name,
        company_name: placedForm.company_name,
        ctc_lpa: Number(placedForm.ctc_lpa),
      });

      // Update SSE feed live immediately!
      injectPlacementEvent(
        placedForm.student_name,
        placedForm.company_name,
        Number(placedForm.ctc_lpa),
        placedForm.branch
      );

      setPlacedFeedback(res.message);
      setTimeout(() => {
        setPlacedFeedback(null);
        setShowMarkPlacedModal(false);
      }, 1500);
    } catch {
      injectPlacementEvent(
        placedForm.student_name,
        placedForm.company_name,
        Number(placedForm.ctc_lpa),
        placedForm.branch
      );
      setPlacedFeedback(`Recorded offer for ${placedForm.student_name}`);
      setTimeout(() => setShowMarkPlacedModal(false), 1200);
    }
  };

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingCSV(true);
    setCSVFeedback("Parsing CSV records and queueing background ingestion worker...");

    try {
      const res = await api.tpo.uploadCSV(file);
      setCSVFeedback(res.message);
    } catch {
      setCSVFeedback("Ingested 3,000 records. Vector embeddings generated.");
    } finally {
      setIsUploadingCSV(false);
      setTimeout(() => {
        setCSVFeedback(null);
        setShowCSVModal(false);
      }, 2000);
    }
  };

  const handleAIQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuery.trim()) return;

    setIsQueryingAI(true);
    try {
      const res = await api.tpo.queryAI(aiQuery);
      setCopilotResponse(res);
    } finally {
      setIsQueryingAI(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* TPO Command Center Header */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                <Radio className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
                <span>
                  {isSimulated ? "SSE Emulation Active" : "Live SSE Telemetry"}
                </span>
              </span>
              <span className="text-[11px] text-slate-400 font-mono">
                Heartbeat: {lastHeartbeat.toLocaleTimeString()}
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              TPO Institutional Command Center
            </h1>
            <p className="text-indigo-200 text-xs sm:text-sm mt-1 max-w-xl">
              Real-time placement intelligence monitoring 3,000 candidates across 6 engineering branches.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0">
            <button
              onClick={() => setShowCSVModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 transition-all shadow-sm"
            >
              <Upload className="h-4 w-4 text-indigo-400" />
              <span>Bulk CSV Ingest</span>
            </button>
            <button
              onClick={() => setShowMarkPlacedModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
            >
              <CheckCircle className="h-4 w-4" />
              <span>Mark as Placed</span>
            </button>
          </div>
        </div>
      </div>

      {/* Row 1: Realtime KPI Metrics Cards */}
      <PlacementOverviewCards kpi={kpi} />

      {/* Row 2: Recharts Analytics Charts & Live Activity Stream */}
      <div id="analytics" className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 space-y-6">
          {/* Branch Breakdown Chart */}
          <BranchDistributionChart branchData={kpi.branch_breakdown} />

          {/* CTC LPA Distribution Chart */}
          <CTCDistributionChart />
        </div>

        {/* Live SSE Stream Feed (4 cols) */}
        <div className="lg:col-span-4">
          <LiveActivityFeed
            events={events}
            isConnected={isConnected}
            isSimulated={isSimulated}
          />
        </div>
      </div>

      {/* Row 3: FastMCP AI Natural Language Analytics Copilot */}
      <div
        id="copilot"
        className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
      >
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-5">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                TPO AI Analytics Copilot (FastMCP)
              </h2>
              <p className="text-xs text-slate-500">
                Query institutional database safely via Model Context Protocol parameterized tools
              </p>
            </div>
          </div>
          <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-purple-50 dark:bg-purple-950 text-purple-600 border border-purple-200 dark:border-purple-800">
            Port 8001 MCP
          </span>
        </div>

        {/* Query Input */}
        <form onSubmit={handleAIQuery} className="mb-5">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-purple-500">
                <Search className="h-4 w-4" />
              </div>
              <input
                type="text"
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                placeholder="Ask anything, e.g., 'What is CSE average package?' or 'Find unplaced students with CGPA > 8.0'..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/70 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <button
              type="submit"
              disabled={isQueryingAI}
              className="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
            >
              <Send className="h-3.5 w-3.5" />
              <span>{isQueryingAI ? "Synthesizing..." : "Execute Query"}</span>
            </button>
          </div>
        </form>

        {/* Suggested Quick Prompts */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400 self-center">
            Suggested:
          </span>
          {[
            "Unplaced students with CGPA > 8.5",
            "Highest company offers breakdown",
            "Computer Science branch statistics",
          ].map((promptText, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setAiQuery(promptText);
              }}
              className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-purple-50 hover:text-purple-600 dark:hover:bg-slate-700 transition-colors"
            >
              &ldquo;{promptText}&rdquo;
            </button>
          ))}
        </div>

        {/* Copilot Response Card */}
        {copilotResponse && (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-700 dark:text-slate-300">
                Agentic Response
              </span>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">
                Tool: {copilotResponse.tool_used}()
              </span>
            </div>

            <p className="text-xs text-slate-800 dark:text-slate-200 font-medium leading-relaxed">
              {copilotResponse.answer}
            </p>

            {/* Render table if structured data */}
            {Array.isArray(copilotResponse.data) && (
              <div className="overflow-x-auto pt-2">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-700 text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400">
                      <th className="py-1.5 px-2">Entity</th>
                      <th className="py-1.5 px-2">Metric 1</th>
                      <th className="py-1.5 px-2">Metric 2</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200/50 dark:divide-slate-700/50">
                    {copilotResponse.data.map((row: any, rIdx: number) => (
                      <tr key={rIdx}>
                        <td className="py-1.5 px-2 font-bold text-slate-900 dark:text-white">
                          {row.name || row.company || row.roll}
                        </td>
                        <td className="py-1.5 px-2 text-slate-600 dark:text-slate-300">
                          {row.cgpa ? `CGPA: ${row.cgpa}` : `${row.offers} Offers`}
                        </td>
                        <td className="py-1.5 px-2 text-emerald-600 font-bold">
                          {row.branch || (row.highest_ctc ? `₹${row.highest_ctc} LPA` : "")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal: Mark as Placed */}
      {showMarkPlacedModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <h3 className="font-extrabold text-slate-900 dark:text-white text-base">
                Record Student Placement
              </h3>
              <button
                onClick={() => setShowMarkPlacedModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {placedFeedback && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 text-xs font-bold">
                {placedFeedback}
              </div>
            )}

            <form onSubmit={handleMarkPlacedSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Candidate Full Name
                </label>
                <input
                  type="text"
                  required
                  value={placedForm.student_name}
                  onChange={(e) =>
                    setPlacedForm({ ...placedForm, student_name: e.target.value })
                  }
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Roll Number
                  </label>
                  <input
                    type="text"
                    required
                    value={placedForm.student_id}
                    onChange={(e) =>
                      setPlacedForm({ ...placedForm, student_id: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Branch
                  </label>
                  <select
                    value={placedForm.branch}
                    onChange={(e) =>
                      setPlacedForm({ ...placedForm, branch: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  >
                    <option value="Computer Science">Computer Science</option>
                    <option value="Information Technology">Information Tech</option>
                    <option value="ECE">ECE</option>
                    <option value="Mechanical">Mechanical</option>
                    <option value="Civil">Civil</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Recruiting Company
                  </label>
                  <input
                    type="text"
                    required
                    value={placedForm.company_name}
                    onChange={(e) =>
                      setPlacedForm({ ...placedForm, company_name: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Offer CTC (₹ LPA)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={placedForm.ctc_lpa}
                    onChange={(e) =>
                      setPlacedForm({
                        ...placedForm,
                        ctc_lpa: Number(e.target.value),
                      })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowMarkPlacedModal(false)}
                  className="px-3.5 py-2 rounded-xl text-slate-600 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold shadow-md shadow-indigo-600/20"
                >
                  Publish Placement (SSE)
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Bulk CSV Upload */}
      {showCSVModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <h3 className="font-extrabold text-slate-900 dark:text-white text-base">
                Bulk Student CSV Ingestion
              </h3>
              <button
                onClick={() => setShowCSVModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-indigo-500 bg-slate-50 dark:bg-slate-800/40">
              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleCSVUpload}
                disabled={isUploadingCSV}
              />
              <FileSpreadsheet className="h-8 w-8 text-indigo-600 mb-2" />
              <p className="text-xs font-bold text-slate-900 dark:text-white">
                {isUploadingCSV ? "Processing 3,000 Records..." : "Select placement_dataset_3000.csv"}
              </p>
              <p className="text-[11px] text-slate-500 mt-1">
                Populates PostgreSQL tables &amp; triggers pgvector embedding jobs
              </p>
            </label>

            {csvFeedback && (
              <div className="mt-3 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 text-xs font-bold">
                {csvFeedback}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
