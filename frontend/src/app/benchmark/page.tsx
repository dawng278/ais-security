"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { BenchmarkSummary } from "@/lib/types";
import { Play, CheckCircle2, XCircle, BarChart3, ShieldCheck } from "lucide-react";

export default function BenchmarkPage() {
  const [benchmarkRes, setBenchmarkRes] = useState<BenchmarkSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRunBenchmark = async () => {
    setLoading(true);
    try {
      const res = await api.runBenchmark();
      setBenchmarkRes(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" /> Security Benchmark Suite
            </h2>
            <p className="text-sm text-slate-400">
              Evaluate Firewall Detection Accuracy, Precision, Recall & FPR against Red-team Datasets.
            </p>
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-sm font-semibold rounded-lg shadow transition flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            {loading ? "Running Suite..." : "Execute Benchmark Suite"}
          </button>
        </div>

        {benchmarkRes && (
          <div className="space-y-6">
            {/* Metrics Overview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Overall Accuracy</div>
                <div className="text-2xl font-black text-emerald-400">
                  {(benchmarkRes.accuracy * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">
                  {benchmarkRes.passed_cases} / {benchmarkRes.total_cases} Cases Passed
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Precision</div>
                <div className="text-2xl font-black text-cyan-400">
                  {(benchmarkRes.precision * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">True Positive Detection</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Recall</div>
                <div className="text-2xl font-black text-teal-400">
                  {(benchmarkRes.recall * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Attack Coverage</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">False Positive Rate</div>
                <div className="text-2xl font-black text-amber-400">
                  {(benchmarkRes.false_positive_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Clean Submissions Control</div>
              </div>
            </div>

            {/* Test Cases Result Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-slate-200">Test Case Execution Breakdown</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
                    <tr>
                      <th className="p-3">Case ID</th>
                      <th className="p-3">Label</th>
                      <th className="p-3">Expected Action</th>
                      <th className="p-3">Actual Action</th>
                      <th className="p-3">Risk Score</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {benchmarkRes.case_results.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-800/40 transition">
                        <td className="p-3 font-mono text-cyan-400">{c.id}</td>
                        <td className="p-3 font-mono">{c.label}</td>
                        <td className="p-3 uppercase">{c.expected_action}</td>
                        <td className="p-3 uppercase text-emerald-400">{c.actual_action}</td>
                        <td className="p-3 font-mono text-amber-400">
                          {(c.risk_score * 100).toFixed(0)}%
                        </td>
                        <td className="p-3">
                          {c.passed ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                              <CheckCircle2 className="w-4 h-4" /> PASSED
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-rose-400 font-bold">
                              <XCircle className="w-4 h-4" /> FAILED
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
