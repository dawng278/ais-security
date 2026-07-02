"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { BenchmarkReportV2 } from "@/lib/types";
import { Play, CheckCircle2, XCircle, BarChart3, ShieldCheck, AlertOctagon } from "lucide-react";

export default function BenchmarkPage() {
  const [report, setReport] = useState<BenchmarkReportV2 | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRunBenchmarkV2 = async () => {
    setLoading(true);
    try {
      const res = await api.runBenchmarkV2();
      setReport(res);
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
              <BarChart3 className="w-5 h-5 text-teal-400" /> Multi-Source IELTS Benchmark Suite v2
            </h2>
            <p className="text-sm text-slate-400">
              Evaluate Macro F1, Precision, Recall, FPR, and Attack Breakdown across IELTS Injected Datasets.
            </p>
          </div>

          <button
            onClick={handleRunBenchmarkV2}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white text-sm font-semibold rounded-lg shadow transition flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            {loading ? "Running Benchmark v2..." : "Execute Benchmark v2 Suite"}
          </button>
        </div>

        {report && (
          <div className="space-y-6">
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Macro F1 Score</div>
                <div className="text-2xl font-black text-teal-400">
                  {(report.macro_f1 * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">
                  Passed {report.passed_cases} / {report.total_cases} Evaluation Cases
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Precision / Recall</div>
                <div className="text-2xl font-black text-cyan-400">
                  {(report.precision * 100).toFixed(0)}% / {(report.recall * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Detector Accuracy & Coverage</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">False Positive Rate</div>
                <div className="text-2xl font-black text-emerald-400">
                  {(report.false_positive_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Clean Essay Utility Preservation</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                <div className="text-xs text-slate-400">Under-Block Rate</div>
                <div className="text-2xl font-black text-amber-400">
                  {(report.under_block_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Missed Vulnerability Index</div>
              </div>
            </div>

            {/* Attack Category Breakdown */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Accuracy by Attack Category</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {Object.entries(report.by_attack_type).map(([atk, val]) => (
                  <div key={atk} className="bg-slate-950 border border-slate-800 p-3 rounded-lg flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-300">{atk}</span>
                    <span className="font-bold text-teal-400">{(val.accuracy * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Failure Cases Table */}
            {report.failure_cases.length > 0 ? (
              <div className="bg-slate-900 border border-rose-900/40 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-semibold text-rose-400 flex items-center gap-1.5">
                  <AlertOctagon className="w-4 h-4" /> Failure Analysis Log
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                      <tr>
                        <th className="p-2.5">Sample ID</th>
                        <th className="p-2.5">Attack Type</th>
                        <th className="p-2.5">Expected</th>
                        <th className="p-2.5">Predicted</th>
                        <th className="p-2.5">Error Type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {report.failure_cases.map((f) => (
                        <tr key={f.sample_id}>
                          <td className="p-2.5 font-mono text-cyan-400">{f.sample_id}</td>
                          <td className="p-2.5 font-mono">{f.attack_type}</td>
                          <td className="p-2.5 uppercase">{f.expected_action}</td>
                          <td className="p-2.5 uppercase text-rose-400">{f.predicted_action}</td>
                          <td className="p-2.5 font-bold text-amber-400">{f.error_type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-emerald-950/30 border border-emerald-800/40 rounded-xl text-xs text-emerald-300 text-center flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Zero failure cases detected across benchmark v2 evaluation samples.
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
