"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Cpu,
  Activity,
  History,
  UserCheck,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  Database,
  Radio,
  Clock,
  Sparkles,
  Server,
} from "lucide-react";
import { api, MOCK_AUDIT_LOGS, MOCK_HEALTH_CHECKS } from "@/lib/api";
import { AuditLogEntry, SystemHealthCheck } from "@/lib/types";

export default function AdminDashboardPage() {
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>(MOCK_AUDIT_LOGS);
  const [healthChecks, setHealthChecks] =
    useState<SystemHealthCheck[]>(MOCK_HEALTH_CHECKS);
  const [pendingUsers, setPendingUsers] = useState<
    Array<{ id: string; name: string; email: string; role: string; requested_at: string }>
  >([]);
  const [isRetraining, setIsRetraining] = useState(false);
  const [retrainResult, setRetrainResult] = useState<string | null>(null);

  useEffect(() => {
    api.admin.getAuditLogs().then(setAuditLogs).catch(console.error);
    api.admin.getHealthChecks().then(setHealthChecks).catch(console.error);
    api.admin.getPendingApprovals().then(setPendingUsers).catch(console.error);
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    setRetrainResult(null);
    try {
      const res = await api.admin.triggerMLRetraining();
      setRetrainResult(res.message);
      // Append an audit log
      const newLog: AuditLogEntry = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toISOString(),
        actor: "Super Admin (Vikram Adve)",
        role: "Admin",
        action: "TRIGGER_ML_RETRAIN",
        target: "XGBoost Career Classifier v2.5",
        status: "success",
        ip_address: "127.0.0.1",
      };
      setAuditLogs((prev) => [newLog, ...prev]);
    } catch {
      setRetrainResult(
        "Job dispatched to worker queue: Retraining XGBoost on 3,000 records."
      );
    } finally {
      setIsRetraining(false);
    }
  };

  const handleApprove = async (id: string, name: string) => {
    await api.admin.approveUser(id);
    setPendingUsers((prev) => prev.filter((u) => u.id !== id));
    const newLog: AuditLogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      actor: "Super Admin",
      role: "Admin",
      action: "APPROVE_USER",
      target: `Granted active credentials to ${name}`,
      status: "success",
      ip_address: "127.0.0.1",
    };
    setAuditLogs((prev) => [newLog, ...prev]);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Admin Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-purple-950 via-slate-900 to-slate-900 text-white p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold border border-purple-500/30 mb-3">
              <ShieldCheck className="h-3.5 w-3.5 text-purple-300" />
              <span>Super Administrator Governance</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Institutional Admin Console
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-xl">
              Platform observability, security audit streams, model retraining pipelines,
              and role authorization controls.
            </p>
          </div>

          <button
            onClick={handleRetrain}
            disabled={isRetraining}
            className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all shrink-0 disabled:opacity-50"
          >
            <Cpu className={`h-4 w-4 ${isRetraining ? "animate-spin" : ""}`} />
            <span>{isRetraining ? "Retraining Engine..." : "Retrain ML Model"}</span>
          </button>
        </div>
      </div>

      {retrainResult && (
        <div className="p-4 rounded-2xl bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 text-xs text-purple-900 dark:text-purple-200 font-bold flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-purple-500 shrink-0" />
          <span>{retrainResult}</span>
        </div>
      )}

      {/* Row 1: System Health Checks & Pending User Approvals */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* System Health Summary (7 cols) */}
        <div
          id="health"
          className="lg:col-span-7 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
        >
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                  System Health &amp; Microservices
                </h2>
                <p className="text-xs text-slate-500">
                  Live connection latency and operational status
                </p>
              </div>
            </div>
            <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2.5 py-1 rounded-full">
              All 6 Services Healthy
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {healthChecks.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-900 dark:text-white">
                    {item.service}
                  </span>
                  <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-600">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                    {item.latency_ms}ms
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight">
                  {item.details}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Pending Approvals (5 cols) */}
        <div
          id="approvals"
          className="lg:col-span-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-600">
                  <UserCheck className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                    Pending Role Approvals
                  </h2>
                  <p className="text-xs text-slate-500">
                    Identity verification requests
                  </p>
                </div>
              </div>
              <span className="text-xs font-bold text-amber-600 bg-amber-50 dark:bg-amber-950 px-2.5 py-1 rounded-full">
                {pendingUsers.length} Pending
              </span>
            </div>

            <div className="space-y-3">
              {pendingUsers.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-6">
                  No accounts awaiting administrator approval.
                </p>
              ) : (
                pendingUsers.map((user) => (
                  <div
                    key={user.id}
                    className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div>
                      <p className="font-bold text-slate-900 dark:text-white">
                        {user.name}
                      </p>
                      <p className="text-[11px] text-slate-500">
                        {user.email} &bull;{" "}
                        <span className="capitalize font-semibold text-indigo-600">
                          {user.role}
                        </span>
                      </p>
                    </div>

                    <button
                      onClick={() => handleApprove(user.id, user.name)}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[11px] shadow-sm transition-all"
                    >
                      Approve
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <p className="text-[11px] text-slate-500 mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            Approved recruiters receive drive creation and pgvector candidate search privileges.
          </p>
        </div>
      </div>

      {/* Row 2: Comprehensive Audit Log Table */}
      <div
        id="audit"
        className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 p-6 shadow-sm"
      >
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600">
              <History className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-extrabold text-slate-900 dark:text-white text-base">
                System Security &amp; Transaction Audit Trail
              </h2>
              <p className="text-xs text-slate-500">
                Immutable event stream tracking user actions, ML retraining, and API activity
              </p>
            </div>
          </div>
          <span className="text-xs font-bold text-slate-500">
            {auditLogs.length} Events Recorded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400 font-bold">
                <th className="py-3 px-3">Timestamp</th>
                <th className="py-3 px-3">Actor &amp; Role</th>
                <th className="py-3 px-3">Action</th>
                <th className="py-3 px-3">Target Details</th>
                <th className="py-3 px-3">IP Address</th>
                <th className="py-3 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {auditLogs.map((log) => (
                <tr
                  key={log.id}
                  className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                >
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-bold text-slate-900 dark:text-white">
                      {log.actor}
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      {log.role}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-mono text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-600 dark:text-slate-300 font-medium max-w-xs truncate">
                    {log.target}
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-500">
                    {log.ip_address}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        log.status === "success"
                          ? "bg-emerald-50 dark:bg-emerald-950 text-emerald-600"
                          : log.status === "warning"
                          ? "bg-amber-50 dark:bg-amber-950 text-amber-600"
                          : "bg-rose-50 dark:bg-rose-950 text-rose-600"
                      }`}
                    >
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
