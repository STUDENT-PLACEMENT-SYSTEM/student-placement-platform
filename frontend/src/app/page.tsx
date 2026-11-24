"use client";

import React from "react";
import Link from "next/link";
import {
  GraduationCap,
  Building2,
  BarChart3,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Cpu,
  Database,
  Radio,
  FileCheck2,
  CheckCircle2,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { UserRole } from "@/lib/types";

export default function LandingPage() {
  const { loginAs } = useAuth();

  const demoRoles: Array<{
    role: UserRole;
    title: string;
    description: string;
    icon: React.ElementType;
    badge: string;
    buttonColor: string;
    features: string[];
    sampleUser: string;
  }> = [
    {
      role: "student",
      title: "Student Portal",
      description:
        "Predict placement odds with XGBoost, extract resume skills via LangGraph, and generate a 4-week preparation roadmap.",
      icon: GraduationCap,
      badge: "Candidate AI",
      buttonColor: "bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/20",
      sampleUser: "Rohan Sharma (2021CS045 - CGPA 8.65)",
      features: [
        "ML Placement Probability Gauge (88.4%)",
        "LangGraph PDF Resume Parser",
        "4-Week AI Roadmap against Amazon SDE-1",
        "One-click Drive Application",
      ],
    },
    {
      role: "recruiter",
      title: "Recruiter Portal",
      description:
        "Create placement drives and conduct pgvector semantic candidate discovery with 1536-dimensional HNSW cosine retrieval.",
      icon: Building2,
      badge: "Vector Hiring",
      buttonColor: "bg-amber-600 hover:bg-amber-700 text-white shadow-amber-500/20",
      sampleUser: "Sarah Jenkins (Amazon AWS Campus Talent)",
      features: [
        "Instant Drive Creation & Eligibility Filters",
        "pgvector Semantic Candidate Search",
        "Interactive Match Similarity Scores (94%)",
        "Shortlist & Interview Status Pipeline",
      ],
    },
    {
      role: "tpo",
      title: "TPO Command Center",
      description:
        "Real-time institutional KPI stream, SSE push notifications, FastMCP natural language querying, and bulk CSV ingestion.",
      icon: BarChart3,
      badge: "Real-Time SSE",
      buttonColor: "bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/20",
      sampleUser: "Dr. Priya Nair (Head of Corporate Relations)",
      features: [
        "Server-Sent Events (SSE) Live Feed",
        "Recharts Branch & CTC Distributions",
        "Natural Language AI Analytics Copilot",
        "Bulk 3,000 Student Ingestion & Mark-Placed",
      ],
    },
    {
      role: "admin",
      title: "Super Admin Console",
      description:
        "Manage security audits, trigger asynchronous XGBoost retraining, monitor system health checks, and approve pending accounts.",
      icon: ShieldCheck,
      badge: "Platform Ops",
      buttonColor: "bg-purple-600 hover:bg-purple-700 text-white shadow-purple-500/20",
      sampleUser: "Prof. Vikram Adve (Chief Technology Admin)",
      features: [
        "Audit Log Stream & Security Monitoring",
        "Trigger Asynchronous ML Retraining",
        "Service Health: Postgres, Redis, MinIO, MCP",
        "Pending Role Approvals Guard",
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-200/80 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <GraduationCap className="h-5 w-5" />
          </div>
          <div>
            <span className="font-black text-lg text-slate-900 dark:text-white tracking-tight leading-none block">
              PlacementIQ
            </span>
            <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest block mt-0.5">
              Next-Gen Career Intelligence
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-3 py-1.5 rounded-full border border-emerald-200 dark:border-emerald-900/60">
            <Radio className="h-3.5 w-3.5 animate-pulse" />
            <span>SSE Stream Live</span>
          </div>
          <Link
            href="/login"
            className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 text-white dark:bg-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 transition-all shadow-sm"
          >
            Manual Login
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 px-6 max-w-7xl mx-auto text-center w-full">
        {/* Glow backdrop */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/15 to-pink-500/20 blur-3xl -z-10 rounded-full pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-300 border border-indigo-200/80 dark:border-indigo-800 mb-6 shadow-sm">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Full-Stack AI Architecture: FastAPI + pgvector + LangGraph + SSE</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white tracking-tight leading-tight max-w-4xl mx-auto">
          Student Placement Analytics &amp; Career Intelligence
        </h1>

        <p className="mt-5 text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
          Empowering colleges with machine-learning career predictions, semantic
          pgvector resume filtering, and real-time Server-Sent Events KPI telemetry.
        </p>

        {/* Quick Launch Role Grid */}
        <div className="mt-12 text-left">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                Select a Role to Launch Interactive Demo
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Click any persona below to enter with pre-authenticated credentials
              </p>
            </div>
            <span className="hidden sm:inline-block text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-3 py-1 rounded-full">
              4 Fully Operational Portals
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {demoRoles.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.role}
                  className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 flex flex-col justify-between shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                        <Icon className="h-6 w-6" />
                      </div>
                      <span className="text-[10px] font-bold tracking-wider uppercase px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {item.badge}
                      </span>
                    </div>

                    <h3 className="font-extrabold text-slate-900 dark:text-white text-lg">
                      {item.title}
                    </h3>

                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                      {item.description}
                    </p>

                    <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 space-y-1.5">
                      {item.features.map((feat, fIdx) => (
                        <div
                          key={fIdx}
                          className="flex items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-300 font-medium"
                        >
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                          <span className="truncate">{feat}</span>
                        </div>
                      ))}
                    </div>

                    <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-3 italic truncate">
                      Demo Profile: {item.sampleUser}
                    </p>
                  </div>

                  <div className="mt-6 pt-4">
                    <button
                      onClick={() => loginAs(item.role)}
                      className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all shadow-md ${item.buttonColor}`}
                    >
                      <span>Launch as {item.role.toUpperCase()}</span>
                      <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Architecture Highlights Bar */}
      <section className="border-t border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 py-10 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="p-4">
            <div className="h-10 w-10 mx-auto rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 flex items-center justify-center mb-2">
              <Database className="h-5 w-5" />
            </div>
            <p className="font-bold text-slate-900 dark:text-white text-sm">PostgreSQL 16 + pgvector</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">1536-dim HNSW Cosine Index</p>
          </div>
          <div className="p-4">
            <div className="h-10 w-10 mx-auto rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600 flex items-center justify-center mb-2">
              <Radio className="h-5 w-5" />
            </div>
            <p className="font-bold text-slate-900 dark:text-white text-sm">Redis 7.2 Pub/Sub &amp; SSE</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Real-time KPI streaming</p>
          </div>
          <div className="p-4">
            <div className="h-10 w-10 mx-auto rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-600 flex items-center justify-center mb-2">
              <Cpu className="h-5 w-5" />
            </div>
            <p className="font-bold text-slate-900 dark:text-white text-sm">XGBoost &amp; LangGraph</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Career prediction &amp; 4-wk sprints</p>
          </div>
          <div className="p-4">
            <div className="h-10 w-10 mx-auto rounded-xl bg-purple-50 dark:bg-purple-950 text-purple-600 flex items-center justify-center mb-2">
              <FileCheck2 className="h-5 w-5" />
            </div>
            <p className="font-bold text-slate-900 dark:text-white text-sm">FastMCP Read-Only Copilot</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Natural language query agent</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200/80 dark:border-slate-800 bg-slate-100/60 dark:bg-slate-950 py-6 px-6 text-center text-xs text-slate-500">
        PlacementIQ &copy; {new Date().getFullYear()} — Institutional Placement Analytics &amp; Career Intelligence Platform.
      </footer>
    </div>
  );
}
