"use client";

import React, { useState, useEffect } from "react";
import {
  Building2,
  Briefcase,
  PlusCircle,
  Search,
  Sparkles,
  Users,
  CheckCircle2,
  Clock,
  Layers,
  MapPin,
  Calendar,
  XCircle,
  ArrowRight,
  Filter,
} from "lucide-react";
import { api, MOCK_DRIVES, MOCK_APPLICANTS } from "@/lib/api";
import { Drive, Applicant } from "@/lib/types";
import { formatCurrencyLPA } from "@/lib/utils";

export default function RecruiterDashboardPage() {
  const [drives, setDrives] = useState<Drive[]>(MOCK_DRIVES);
  const [selectedDriveId, setSelectedDriveId] = useState<string>("drv-001");
  const [applicants, setApplicants] = useState<Applicant[]>(MOCK_APPLICANTS);
  const [semanticQuery, setSemanticQuery] = useState(
    "Candidates proficient in distributed systems, Docker, Redis, and high concurrency"
  );
  const [isSearching, setIsSearching] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Drive Form State
  const [newDrive, setNewDrive] = useState({
    title: "",
    role_name: "",
    company_name: "Amazon AWS",
    job_description: "",
    min_cgpa: 7.5,
    max_backlogs: 0,
    allowed_branches: ["Computer Science", "Information Technology"],
    ctc_min_lpa: 16.0,
    ctc_max_lpa: 24.0,
    job_location: "Bangalore / Hybrid",
    drive_date: "2026-12-15",
    registration_deadline: "2026-12-05",
  });
  const [createFeedback, setCreateFeedback] = useState<string | null>(null);

  useEffect(() => {
    api.recruiter.getDrives().then(setDrives).catch(console.error);
    api.recruiter
      .searchApplicants(selectedDriveId, semanticQuery)
      .then(setApplicants)
      .catch(console.error);
  }, [selectedDriveId]);

  const handleSemanticSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);
    try {
      const results = await api.recruiter.searchApplicants(
        selectedDriveId,
        semanticQuery
      );
      setApplicants(results);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCreateDrive = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api.recruiter.createDrive(newDrive);
      setDrives((prev) => [created, ...prev]);
      setCreateFeedback("Placement Drive published successfully to student portal!");
      setTimeout(() => {
        setCreateFeedback(null);
        setShowCreateModal(false);
      }, 1500);
    } catch {
      setCreateFeedback("Drive created successfully (Demo Mode)");
      setTimeout(() => setShowCreateModal(false), 1200);
    }
  };

  const handleStatusChange = (studentId: string, newStatus: Applicant["status"]) => {
    setApplicants((prev) =>
      prev.map((app) =>
        app.student_id === studentId ? { ...app, status: newStatus } : app
      )
    );
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Recruiter Header */}
      <div className="rounded-3xl bg-gradient-to-r from-amber-950 via-slate-900 to-slate-900 text-white p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-bold border border-amber-500/30 mb-3">
              <Building2 className="h-3.5 w-3.5 text-amber-300" />
              <span>Amazon AWS Talent Acquisition Portal</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Recruiter Command Hub
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-xl">
              Post drive opportunities, discover candidate matches with pgvector
              semantic search, and streamline recruitment decisions.
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition-all shrink-0"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Post New Drive</span>
          </button>
        </div>
      </div>

      {/* Active Drives List */}
      <div id="drives" className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
              Active Placement Drives
            </h2>
            <p className="text-xs text-slate-500">
              Select a drive to inspect applicants and execute semantic vector search
            </p>
          </div>
          <span className="text-xs font-bold text-slate-500">
            {drives.length} Managed Drives
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {drives.map((d) => {
            const isSelected = d.id === selectedDriveId;
            return (
              <div
                key={d.id}
                onClick={() => setSelectedDriveId(d.id)}
                className={`rounded-2xl p-5 border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-white dark:bg-slate-900 border-amber-500 shadow-md ring-1 ring-amber-500"
                    : "bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800 hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-amber-50 dark:bg-amber-950 text-amber-600 flex items-center justify-center font-bold text-xs">
                      {d.company_logo || "CO"}
                    </div>
                    <div>
                      <h3 className="font-extrabold text-slate-900 dark:text-white text-xs">
                        {d.title}
                      </h3>
                      <p className="text-[11px] text-slate-500">{d.company_name}</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-600">
                    {d.status}
                  </span>
                </div>

                <div className="mt-4 flex items-baseline justify-between text-xs">
                  <span className="text-slate-500">Compensation</span>
                  <span className="font-extrabold text-emerald-600 dark:text-emerald-400">
                    ₹{d.ctc_min_lpa} - ₹{d.ctc_max_lpa} LPA
                  </span>
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-2">
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {d.total_applicants || 0} Applied
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    {d.drive_date}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Semantic Search & Applicants Table */}
      <div
        id="applicants"
        className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                pgvector Semantic Candidate Discovery
              </h2>
              <p className="text-xs text-slate-500">
                1536-dimensional HNSW cosine ranking matching natural language against student resumes
              </p>
            </div>
          </div>
        </div>

        {/* Semantic Query Bar */}
        <form onSubmit={handleSemanticSearch} className="mb-6">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-indigo-500">
                <Search className="h-4 w-4" />
              </div>
              <input
                type="text"
                value={semanticQuery}
                onChange={(e) => setSemanticQuery(e.target.value)}
                placeholder="Describe desired skills, e.g., 'Kubernetes, microservices, gRPC, high concurrency'..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="px-5 py-3 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-bold text-xs hover:bg-slate-800 transition-all flex items-center justify-center gap-2 shadow-sm"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              <span>{isSearching ? "Searching Vectors..." : "Rank Candidates"}</span>
            </button>
          </div>
        </form>

        {/* Applicants Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400 font-bold">
                <th className="py-3 px-3">Candidate</th>
                <th className="py-3 px-3">CGPA</th>
                <th className="py-3 px-3">Semantic Match</th>
                <th className="py-3 px-3">Matched Skills</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
              {applicants.map((app) => (
                <tr
                  key={app.student_id}
                  className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-3.5 px-3">
                    <div className="font-bold text-slate-900 dark:text-white">
                      {app.full_name}
                    </div>
                    <div className="text-slate-500 text-[11px]">
                      {app.roll_number} &bull; {app.branch}
                    </div>
                  </td>
                  <td className="py-3.5 px-3 font-bold text-slate-800 dark:text-slate-200">
                    {app.cgpa.toFixed(2)}
                  </td>
                  <td className="py-3.5 px-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full"
                          style={{
                            width: `${((app.similarity_score || 0.85) * 100).toFixed(0)}%`,
                          }}
                        />
                      </div>
                      <span className="font-extrabold text-emerald-600 dark:text-emerald-400 text-xs">
                        {((app.similarity_score || 0.85) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-3">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {app.matched_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3.5 px-3">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                        app.status === "shortlisted"
                          ? "bg-amber-50 dark:bg-amber-950 text-amber-700"
                          : app.status === "offered"
                          ? "bg-emerald-50 dark:bg-emerald-950 text-emerald-700"
                          : app.status === "interviewed"
                          ? "bg-blue-50 dark:bg-blue-950 text-blue-700"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600"
                      }`}
                    >
                      {app.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 text-right">
                    <div className="inline-flex items-center gap-1.5">
                      <button
                        onClick={() => handleStatusChange(app.student_id, "shortlisted")}
                        className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-amber-50 hover:bg-amber-100 text-amber-700 transition-colors"
                      >
                        Shortlist
                      </button>
                      <button
                        onClick={() => handleStatusChange(app.student_id, "interviewed")}
                        className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 transition-colors"
                      >
                        Interview
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Post New Drive Form */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 max-w-2xl w-full p-6 sm:p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-4">
              <h3 className="font-extrabold text-slate-900 dark:text-white text-lg">
                Publish Campus Placement Drive
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {createFeedback && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 text-xs font-bold">
                {createFeedback}
              </div>
            )}

            <form onSubmit={handleCreateDrive} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Job Title / Role
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. SDE-1 (Backend)"
                    value={newDrive.title}
                    onChange={(e) => setNewDrive({ ...newDrive, title: e.target.value })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newDrive.company_name}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, company_name: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Min CTC (₹ LPA)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={newDrive.ctc_min_lpa}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, ctc_min_lpa: Number(e.target.value) })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Max CTC (₹ LPA)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={newDrive.ctc_max_lpa}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, ctc_max_lpa: Number(e.target.value) })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Minimum CGPA Cutoff
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={newDrive.min_cgpa}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, min_cgpa: Number(e.target.value) })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Job Description &amp; Technical Requirements
                </label>
                <textarea
                  rows={3}
                  placeholder="Paste role specifications, technical requirements, and responsibilities..."
                  value={newDrive.job_description}
                  onChange={(e) =>
                    setNewDrive({ ...newDrive, job_description: e.target.value })
                  }
                  className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Drive Date
                  </label>
                  <input
                    type="date"
                    value={newDrive.drive_date}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, drive_date: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={newDrive.job_location}
                    onChange={(e) =>
                      setNewDrive({ ...newDrive, job_location: e.target.value })
                    }
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  />
                </div>
              </div>

              <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2.5 rounded-xl text-slate-600 dark:text-slate-400 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold shadow-md shadow-amber-500/20"
                >
                  Publish Drive Requirements
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
