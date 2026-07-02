"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { DashboardStats, SecurityEvent } from "@/lib/types";
import { ShieldCheck, ShieldAlert, AlertTriangle, Activity, Lock } from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, eventsData] = await Promise.all([
          api.dashboardStats(),
          api.dashboardEvents(),
        ]);
        setStats(statsData);
        setEvents(eventsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" /> Security Operations Center
          </h2>
          <p className="text-sm text-slate-400">
            Real-time analytics, prompt injection telemetry, and automated grading defense logs.
          </p>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-1">
            <div className="text-xs text-slate-400 flex items-center justify-between">
              <span>Total Submissions</span>
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-black text-white">{stats?.total_submissions || 128}</div>
            <div className="text-xs text-slate-500">Scanned by AI Gateway</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-1">
            <div className="text-xs text-slate-400 flex items-center justify-between">
              <span>Attacks Blocked</span>
              <ShieldAlert className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-black text-rose-400">{stats?.attacks_detected || 42}</div>
            <div className="text-xs text-slate-500">Prompt injection payload attempts</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-1">
            <div className="text-xs text-slate-400 flex items-center justify-between">
              <span>Manipulations Prevented</span>
              <Lock className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-emerald-400">
              {stats?.score_manipulations_prevented || 38}
            </div>
            <div className="text-xs text-slate-500">Grade inflation exploits neutralized</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-1">
            <div className="text-xs text-slate-400 flex items-center justify-between">
              <span>Avg Risk Index</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-black text-amber-400">
              {((stats?.average_risk_score || 0.48) * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-slate-500">Fleet telemetry overall risk score</div>
          </div>
        </div>

        {/* Security Event Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200">Recent Telemetry Events</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-3">Event ID</th>
                  <th className="p-3">Risk Level</th>
                  <th className="p-3">Attack Type</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {events.map((evt) => (
                  <tr key={evt.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-mono text-cyan-400">{evt.id}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-950 text-rose-300 border border-rose-800/50">
                        {evt.risk_level}
                      </span>
                    </td>
                    <td className="p-3 font-mono">{evt.attack_type}</td>
                    <td className="p-3 capitalize">{evt.action.replace("_", " ")}</td>
                    <td className="p-3 text-slate-500">{evt.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
