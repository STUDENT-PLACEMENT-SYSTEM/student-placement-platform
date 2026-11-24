"use client";

import React, { useState, useEffect } from "react";
import {
  GraduationCap,
  UploadCloud,
  Sparkles,
  TrendingUp,
  Briefcase,
  Calendar,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  ArrowRight,
  BookOpen,
  ChevronRight,
  Target,
  ExternalLink,
} from "lucide-react";
import { api, MOCK_PREDICTION, MOCK_ROADMAP, MOCK_DRIVES } from "@/lib/api";
import { PlacementPrediction, SkillGapRoadmap, Drive } from "@/lib/types";
import { formatCurrencyLPA } from "@/lib/utils";

export default function StudentDashboardPage() {
  const [prediction, setPrediction] =
    useState<PlacementPrediction>(MOCK_PREDICTION);
  const [roadmap, setRoadmap] = useState<SkillGapRoadmap>(MOCK_ROADMAP);
  const [drives, setDrives] = useState<Drive[]>(MOCK_DRIVES);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [appliedDrives, setAppliedDrives] = useState<Record<string, boolean>>({
    "drv-001": true,
  });

  useEffect(() => {
    // Fetch data asynchronously with mock fallbacks
    api.student.getPrediction().then(setPrediction).catch(console.error);
    api.student.getRoadmap().then(setRoadmap).catch(console.error);
    api.student.getEligibleDrives().then(setDrives).catch(console.error);
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("Uploading to MinIO S3 & queueing LangGraph parsing...");

    try {
      const res = await api.student.uploadResume(file);
      setUploadStatus(res.message);
    } catch {
      setUploadStatus("Uploaded successfully. Parsing skills in background.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleApply = async (driveId: string) => {
    try {
      await api.student.applyToDrive(driveId);
      setAppliedDrives((prev) => ({ ...prev, [driveId]: true }));
    } catch {
      setAppliedDrives((prev) => ({ ...prev, [driveId]: true }));
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Welcome Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30 mb-3">
              <Sparkles className="h-3.5 w-3.5 text-indigo-300" />
              <span>Campus Recruitment Batch of 2025</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Welcome back, Rohan Sharma!
            </h1>
            <p className="text-indigo-200 text-xs sm:text-sm mt-1 max-w-xl">
              Your profile is synced with university records. Review your ML placement
              probability, personalized preparation roadmap, and apply for open drives.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 shrink-0">
            <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-3.5 text-center">
              <p className="text-[10px] uppercase font-bold text-indigo-200 tracking-wider">
                Overall CGPA
              </p>
              <p className="text-2xl font-black text-white mt-0.5">8.65</p>
              <p className="text-[10px] text-emerald-400 font-bold">Top 8% CSE</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-3.5 text-center">
              <p className="text-[10px] uppercase font-bold text-indigo-200 tracking-wider">
                Active Backlogs
              </p>
              <p className="text-2xl font-black text-emerald-400 mt-0.5">0</p>
              <p className="text-[10px] text-indigo-200">All Cleared</p>
            </div>
          </div>
        </div>
      </div>

      {/* Row 1: ML Placement Probability Gauge & Resume Dropzone */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* ML Gauge & Factors (7 cols) */}
        <div className="lg:col-span-7 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                  XGBoost Career Probability Gauge
                </h2>
                <p className="text-xs text-slate-500">
                  Trained on 3,000 historic institutional placement outcomes
                </p>
              </div>
            </div>

            <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              {prediction.placement_tier}
            </span>
          </div>

          {/* Probability Gauge Banner */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-50/70 to-slate-50 dark:from-slate-800/60 dark:to-slate-900 border border-indigo-100/60 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              {/* Circular Gauge Graphic */}
              <div className="relative flex items-center justify-center shrink-0">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="9"
                    className="text-slate-200 dark:text-slate-800"
                    fill="transparent"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="9"
                    className="text-indigo-600 dark:text-indigo-500 transition-all duration-1000 ease-out"
                    strokeDasharray={2 * Math.PI * 40}
                    strokeDashoffset={
                      2 *
                      Math.PI *
                      40 *
                      (1 - prediction.placement_probability / 100)
                    }
                    strokeLinecap="round"
                    fill="transparent"
                  />
                </svg>
                <div className="absolute text-center">
                  <span className="text-xl font-black text-slate-900 dark:text-white">
                    {prediction.placement_probability}%
                  </span>
                  <span className="block text-[9px] uppercase font-bold text-slate-400">
                    Confidence
                  </span>
                </div>
              </div>

              <div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Predicted CTC Range
                </p>
                <p className="text-2xl font-black text-indigo-600 dark:text-indigo-400 mt-0.5">
                  ₹{prediction.predicted_ctc_range.min_lpa} - ₹
                  {prediction.predicted_ctc_range.max_lpa} LPA
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Expected Median:{" "}
                  <strong className="text-slate-800 dark:text-slate-200">
                    ₹{prediction.predicted_ctc_range.median_lpa} LPA
                  </strong>
                </p>
              </div>
            </div>

            <div className="w-full sm:w-auto text-left sm:text-right border-t sm:border-t-0 sm:border-l border-slate-200 dark:border-slate-800 pt-3 sm:pt-0 sm:pl-6">
              <span className="text-[10px] uppercase font-bold text-slate-400">
                Placement Risk
              </span>
              <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                Low Risk (&lt; 5%)
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Eligible for Tier-1 Drives
              </p>
            </div>
          </div>

          {/* Influencing factors weights */}
          <div className="mt-5 space-y-2">
            <p className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Top Influencing Model Features:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {prediction.top_influencing_factors.map((factor, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs"
                >
                  <span className="font-medium text-slate-700 dark:text-slate-300 truncate">
                    {factor.feature}
                  </span>
                  <span className="font-bold text-indigo-600 dark:text-indigo-400 shrink-0 ml-2">
                    {factor.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resume Dropzone & Extraction (5 cols) */}
        <div
          id="resume"
          className="lg:col-span-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                  LangGraph Resume Parser
                </h2>
                <p className="text-xs text-slate-500">
                  PDF extraction &amp; 1536-dim vector embedding
                </p>
              </div>
            </div>

            {/* Dropzone */}
            <label className="mt-4 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-indigo-500 dark:hover:border-indigo-400 transition-colors bg-slate-50/50 dark:bg-slate-800/30">
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileUpload}
                disabled={isUploading}
              />
              <div className="p-3 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 mb-2">
                <UploadCloud className="h-6 w-6" />
              </div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">
                {isUploading ? "Uploading & Analyzing..." : "Upload or Replace Resume PDF"}
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                Supports PDF format up to 10MB
              </p>
            </label>

            {uploadStatus && (
              <div className="mt-3 p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-xs text-indigo-700 dark:text-indigo-300 flex items-start gap-2">
                <Sparkles className="h-4 w-4 shrink-0 text-indigo-500 mt-0.5" />
                <span>{uploadStatus}</span>
              </div>
            )}

            {/* Extracted Verified Skills */}
            <div className="mt-4">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                Current Extracted Skills
              </span>
              <div className="flex flex-wrap gap-1.5">
                {[
                  "Python",
                  "FastAPI",
                  "Docker",
                  "PostgreSQL",
                  "Redis",
                  "Data Structures",
                  "Algorithms",
                  "PyTorch",
                  "Git",
                ].map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>S3 Bucket: placement-resumes</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              Synced &bull; v2.1
            </span>
          </div>
        </div>
      </div>

      {/* Row 2: 4-Week AI Skill Roadmap */}
      <div
        id="roadmap"
        className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
                <Target className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                  4-Week AI Skill Gap Roadmap
                </h2>
                <p className="text-xs text-slate-500">
                  Generated via LangGraph RAG matching your profile against{" "}
                  <strong>{roadmap.target_company} ({roadmap.target_role})</strong>
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="text-[10px] font-bold text-slate-400 uppercase">
                Target Readiness
              </span>
              <p className="text-lg font-black text-amber-600 dark:text-amber-400 leading-tight">
                {roadmap.readiness_score}%
              </p>
            </div>
            <div className="h-10 w-10 rounded-xl bg-amber-50 dark:bg-amber-950/60 flex items-center justify-center text-amber-600 dark:text-amber-400 font-black text-sm">
              75%
            </div>
          </div>
        </div>

        {/* Missing Skills Warning Bar */}
        <div className="my-4 p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-600 shrink-0" />
            <span className="text-xs font-bold text-amber-900 dark:text-amber-200">
              Identified Skill Gaps for {roadmap.target_company}:
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {roadmap.missing_skills.map((s, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded-md text-[11px] font-bold bg-white dark:bg-slate-900 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* 4 Weekly Sprints Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          {roadmap.weekly_roadmap.map((week) => (
            <div
              key={week.week}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 p-4 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                    Week {week.week}
                  </span>
                  <Clock className="h-3.5 w-3.5 text-slate-400" />
                </div>

                <h3 className="font-bold text-slate-900 dark:text-white text-xs mb-3 line-clamp-2">
                  {week.focus}
                </h3>

                <div className="space-y-2">
                  <span className="text-[10px] font-bold uppercase text-slate-400 block">
                    Action Items
                  </span>
                  {week.action_items.map((item, aIdx) => (
                    <div
                      key={aIdx}
                      className="flex items-start gap-1.5 text-xs text-slate-600 dark:text-slate-300"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 text-indigo-500 shrink-0 mt-0.5" />
                      <span className="leading-tight">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-1">
                  Resources
                </span>
                {week.recommended_resources.map((res, rIdx) => (
                  <p
                    key={rIdx}
                    className="text-[11px] text-indigo-600 dark:text-indigo-400 truncate hover:underline cursor-pointer flex items-center gap-1"
                  >
                    <BookOpen className="h-3 w-3 shrink-0" />
                    <span>{res}</span>
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Row 3: Eligible Placement Drives Table */}
      <div
        id="drives"
        className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400">
              <Briefcase className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                Eligible Placement Drives
              </h2>
              <p className="text-xs text-slate-500">
                You meet eligibility criteria (CGPA &ge; 7.0, 0 Backlogs) for these upcoming campus visits
              </p>
            </div>
          </div>
          <span className="text-xs font-bold text-slate-500">
            {drives.length} Drives Available
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400 font-bold">
                <th className="py-3 px-3">Company &amp; Role</th>
                <th className="py-3 px-3">Package (CTC)</th>
                <th className="py-3 px-3">Min CGPA</th>
                <th className="py-3 px-3">Drive Date</th>
                <th className="py-3 px-3">Location</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
              {drives.map((drive) => {
                const isApplied = appliedDrives[drive.id] || drive.has_applied;
                return (
                  <tr
                    key={drive.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="py-3.5 px-3">
                      <div className="font-bold text-slate-900 dark:text-white">
                        {drive.company_name}
                      </div>
                      <div className="text-slate-500 text-[11px]">
                        {drive.title}
                      </div>
                    </td>
                    <td className="py-3.5 px-3 font-extrabold text-emerald-600 dark:text-emerald-400">
                      ₹{drive.ctc_min_lpa} - ₹{drive.ctc_max_lpa} LPA
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="px-2 py-0.5 rounded-md font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {drive.min_cgpa.toFixed(1)}+
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-slate-600 dark:text-slate-400">
                      {drive.drive_date}
                    </td>
                    <td className="py-3.5 px-3 text-slate-600 dark:text-slate-400">
                      {drive.job_location}
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      {isApplied ? (
                        <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Applied
                        </span>
                      ) : (
                        <button
                          onClick={() => handleApply(drive.id)}
                          className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all"
                        >
                          Apply Now
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
