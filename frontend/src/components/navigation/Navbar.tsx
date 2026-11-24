"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Menu,
  GraduationCap,
  Building2,
  BarChart3,
  ShieldCheck,
  Radio,
  LogOut,
  ChevronDown,
  Sparkles,
  UserCheck,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { UserRole } from "@/lib/types";

interface Props {
  onToggleSidebar?: () => void;
  isSSEConnected?: boolean;
}

export function Navbar({ onToggleSidebar, isSSEConnected = true }: Props) {
  const { user, role, loginAs, logout } = useAuth();
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);

  const roles: Array<{ role: UserRole; label: string; icon: React.ElementType; color: string }> = [
    { role: "student", label: "Student Portal", icon: GraduationCap, color: "text-blue-500 bg-blue-50 dark:bg-blue-950/60" },
    { role: "recruiter", label: "Recruiter Portal", icon: Building2, color: "text-amber-500 bg-amber-50 dark:bg-amber-950/60" },
    { role: "tpo", label: "TPO Command Center", icon: BarChart3, color: "text-indigo-500 bg-indigo-50 dark:bg-indigo-950/60" },
    { role: "admin", label: "Super Admin", icon: ShieldCheck, color: "text-purple-500 bg-purple-50 dark:bg-purple-950/60" },
  ];

  const currentRoleConfig = roles.find((r) => r.role === role) || roles[2];

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Mobile hamburger & breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          aria-label="Toggle Navigation Menu"
          className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-600 dark:text-slate-400">
            Platform /
          </span>
          <span className="font-bold text-slate-900 dark:text-white capitalize">
            {role === "tpo" ? "TPO Command Center" : `${role} Workspace`}
          </span>
        </div>
      </div>

      {/* Right Controls: Role Switcher & User Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Real-time SSE indicator */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-900/60">
          <Radio className="h-3 w-3 animate-pulse" />
          <span>Live Stream</span>
        </div>

        {/* Role Quick Switcher Pills (Desktop) */}
        <div className="hidden xl:flex items-center rounded-xl bg-slate-100 dark:bg-slate-800 p-1 border border-slate-200/60 dark:border-slate-700">
          {roles.map((r) => {
            const Icon = r.icon;
            const isSelected = r.role === role;
            return (
              <button
                key={r.role}
                onClick={() => loginAs(r.role)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                  isSelected
                    ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm"
                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span className="capitalize">{r.role}</span>
              </button>
            );
          })}
        </div>

        {/* Role Switcher Dropdown (Mobile / Tablet) */}
        <div className="relative xl:hidden">
          <button
            onClick={() => setIsRoleDropdownOpen(!isRoleDropdownOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-200"
          >
            <currentRoleConfig.icon className="h-3.5 w-3.5 text-indigo-500" />
            <span className="capitalize">{role}</span>
            <ChevronDown className="h-3.5 w-3.5 opacity-60" />
          </button>

          {isRoleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl py-1 z-50">
              <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400">
                Switch Role View
              </div>
              {roles.map((r) => {
                const Icon = r.icon;
                return (
                  <button
                    key={r.role}
                    onClick={() => {
                      loginAs(r.role);
                      setIsRoleDropdownOpen(false);
                    }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-left hover:bg-slate-50 dark:hover:bg-slate-800 ${
                      r.role === role
                        ? "text-indigo-600 font-bold bg-indigo-50/50 dark:bg-indigo-950/30"
                        : "text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{r.label}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* User Badge Profile */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
            {user?.full_name
              ? user.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
              : "U"}
          </div>

          <div className="hidden sm:block text-left">
            <p className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
              {user?.full_name || "User"}
            </p>
            <p className="text-[10px] font-medium text-slate-500 capitalize">
              {user?.role} {user?.branch ? `• ${user.branch}` : ""}
            </p>
          </div>

          {/* Logout button */}
          <button
            onClick={logout}
            title="Log out"
            aria-label="Log out"
            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors ml-1"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
export default Navbar;
