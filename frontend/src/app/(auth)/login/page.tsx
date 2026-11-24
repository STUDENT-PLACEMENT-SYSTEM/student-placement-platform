"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  GraduationCap,
  Building2,
  BarChart3,
  ShieldCheck,
  Lock,
  Mail,
  ArrowRight,
  Sparkles,
  Check,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { UserRole } from "@/lib/types";

export default function LoginPage() {
  const router = useRouter();
  const { loginAs } = useAuth();

  const [email, setEmail] = useState("rohan.sharma@college.edu");
  const [password, setPassword] = useState("DemoPassword123!");
  const [selectedRole, setSelectedRole] = useState<UserRole>("student");
  const [isLoading, setIsLoading] = useState(false);

  const rolePresets: Array<{
    role: UserRole;
    label: string;
    email: string;
    icon: React.ElementType;
    badge: string;
  }> = [
    {
      role: "student",
      label: "Student",
      email: "rohan.sharma@college.edu",
      icon: GraduationCap,
      badge: "2021CS045",
    },
    {
      role: "recruiter",
      label: "Recruiter",
      email: "sarah.j@amazon.com",
      icon: Building2,
      badge: "Amazon AWS",
    },
    {
      role: "tpo",
      label: "TPO Officer",
      email: "priya.nair@college.edu",
      icon: BarChart3,
      badge: "TPO Cell",
    },
    {
      role: "admin",
      label: "Super Admin",
      email: "admin@college.edu",
      icon: ShieldCheck,
      badge: "Root Admin",
    },
  ];

  const handleSelectRole = (roleItem: (typeof rolePresets)[0]) => {
    setSelectedRole(roleItem.role);
    setEmail(roleItem.email);
    setPassword("DemoPassword123!");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      loginAs(selectedRole);
      setIsLoading(false);
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 relative selection:bg-indigo-500 selection:text-white">
      {/* Background glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <GraduationCap className="h-5 w-5" />
          </div>
          <span className="font-black text-xl text-slate-900 dark:text-white tracking-tight">
            PlacementIQ
          </span>
        </Link>
        <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">
          Sign in to your account
        </h2>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Or click any demo profile to instantly prefill authentication credentials
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-slate-900 py-8 px-6 sm:px-10 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl shadow-slate-200/40 dark:shadow-none space-y-6">
          {/* Role Quick Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Quick Role Prefill
            </label>
            <div className="grid grid-cols-2 gap-2">
              {rolePresets.map((preset) => {
                const Icon = preset.icon;
                const isSelected = selectedRole === preset.role;
                return (
                  <button
                    key={preset.role}
                    type="button"
                    onClick={() => handleSelectRole(preset)}
                    className={`flex items-center gap-2 p-2.5 rounded-xl border text-left transition-all ${
                      isSelected
                        ? "border-indigo-600 bg-indigo-50/70 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 shadow-sm ring-1 ring-indigo-600"
                        : "border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    <Icon className="h-4 w-4 shrink-0 text-indigo-500" />
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold truncate leading-tight">
                        {preset.label}
                      </p>
                      <p className="text-[10px] text-slate-600 dark:text-slate-400 truncate">
                        {preset.badge}
                      </p>
                    </div>
                    {isSelected && (
                      <Check className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1"
              >
                Institutional Email Address
              </label>
              <div className="relative rounded-xl shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="name@college.edu"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1"
              >
                Password
              </label>
              <div className="relative rounded-xl shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center text-slate-600 dark:text-slate-400">
                <input
                  type="checkbox"
                  defaultChecked
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                />
                Remember session
              </label>
              <a
                href="#"
                className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
              >
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50"
            >
              <span>{isLoading ? "Authenticating..." : `Sign in as ${selectedRole.toUpperCase()}`}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          {/* Quick Info */}
          <div className="rounded-xl bg-slate-50 dark:bg-slate-800/60 p-3 border border-slate-100 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 flex items-start gap-2">
            <Sparkles className="h-3.5 w-3.5 text-indigo-500 shrink-0 mt-0.5" />
            <span>
              Role-Based Access Control (RBAC) enforces endpoint routing for Student, Recruiter, TPO, and Admin roles.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
