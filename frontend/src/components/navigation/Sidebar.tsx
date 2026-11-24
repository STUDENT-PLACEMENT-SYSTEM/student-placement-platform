"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  GraduationCap,
  Briefcase,
  BarChart3,
  ShieldCheck,
  Compass,
  FileText,
  Building2,
  Users,
  Cpu,
  History,
  CheckCircle,
  HelpCircle,
  Sparkles,
  Layers,
  ChevronRight,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

export function Sidebar({
  isOpen,
  onClose,
}: {
  isOpen?: boolean;
  onClose?: () => void;
}) {
  const pathname = usePathname();
  const { role, user } = useAuth();

  const getNavLinks = (): NavItem[] => {
    switch (role) {
      case "student":
        return [
          { label: "My Career Portal", href: "/student", icon: Compass },
          { label: "Eligible Drives", href: "/student#drives", icon: Briefcase, badge: "4 New" },
          { label: "AI Skill Roadmap", href: "/student#roadmap", icon: Sparkles },
          { label: "Resume Intelligence", href: "/student#resume", icon: FileText },
        ];
      case "recruiter":
        return [
          { label: "Hiring Command", href: "/recruiter", icon: Building2 },
          { label: "Active Drives", href: "/recruiter#drives", icon: Layers },
          { label: "Semantic Search", href: "/recruiter#applicants", icon: Sparkles, badge: "AI pgvector" },
          { label: "Post New Drive", href: "/recruiter#create", icon: Briefcase },
        ];
      case "tpo":
        return [
          { label: "TPO Command Center", href: "/tpo", icon: BarChart3 },
          { label: "Realtime Analytics", href: "/tpo#analytics", icon: Layers },
          { label: "AI Copilot Query", href: "/tpo#copilot", icon: Sparkles, badge: "FastMCP" },
          { label: "Bulk Ingestion (CSV)", href: "/tpo#ingestion", icon: FileText },
          { label: "Record Placement", href: "/tpo#mark-placed", icon: CheckCircle },
        ];
      case "admin":
        return [
          { label: "Admin Console", href: "/admin", icon: ShieldCheck },
          { label: "User Approvals", href: "/admin#approvals", icon: Users, badge: "3 Pending" },
          { label: "Audit Logs", href: "/admin#audit", icon: History },
          { label: "ML Retraining", href: "/admin#retrain", icon: Cpu },
          { label: "System Health", href: "/admin#health", icon: Layers },
        ];
      default:
        return [];
    }
  };

  const navLinks = getNavLinks();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-100 dark:border-slate-800">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-500/20">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <span className="font-extrabold text-slate-900 dark:text-white tracking-tight text-base leading-none block">
                PlacementIQ
              </span>
              <span className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block mt-0.5">
                AI Analytics Platform
              </span>
            </div>
          </Link>
        </div>

        {/* Current Role Context Card */}
        <div className="p-4 mx-4 my-3 rounded-xl bg-gradient-to-br from-indigo-50/70 to-slate-50 dark:from-slate-800/80 dark:to-slate-900/80 border border-indigo-100/60 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 dark:text-slate-400">
              Current Workspace
            </span>
            <span className="capitalize text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
              {role}
            </span>
          </div>
          <p className="font-bold text-xs text-slate-900 dark:text-white mt-1 truncate">
            {user?.full_name || "Authorized User"}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
            {user?.email}
          </p>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold tracking-wider text-slate-600 dark:text-slate-400 uppercase">
            Navigation Menu
          </div>

          {navLinks.map((item, idx) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== `/${role}` && pathname.startsWith(item.href));

            return (
              <Link
                key={idx}
                href={item.href}
                onClick={onClose}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/20"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-4 w-4 ${
                      isActive
                        ? "text-white"
                        : "text-slate-600 dark:text-slate-400"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  {item.badge && (
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        isActive
                          ? "bg-white/20 text-white"
                          : "bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-300"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                  <ChevronRight
                    className={`h-3 w-3 opacity-40 ${
                      isActive ? "text-white" : ""
                    }`}
                  />
                </div>
              </Link>
            );
          })}
        </div>

        {/* Platform Footnote */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400 flex items-center justify-between">
          <span>FastAPI + pgvector + SSE</span>
          <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Online
          </span>
        </div>
      </aside>
    </>
  );
}
export default Sidebar;
