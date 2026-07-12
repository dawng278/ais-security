"use client";

import React, { useCallback, useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { DatasetLineageReport, DataSourceLineage, TransformStage } from "@/lib/types";
import {
  GitBranch,
  Database,
  Layers,
  ShieldCheck,
  FileCode,
  CheckCircle2,
  Copy,
  Filter,
  PieChart,
  Hash,
  Sparkles,
} from "lucide-react";

export default function DataLineagePage() {
  const [report, setReport] = useState<DatasetLineageReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [isDemoFallback, setIsDemoFallback] = useState(false);

  const fetchLineageData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getLineageReport();
      setReport(res);
      setIsDemoFallback(res.dataset_version?.includes("demo") || false);
    } catch (err) {
      console.error("Failed to fetch lineage report from API, fallback to seeded local demo data:", err);
      setIsDemoFallback(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(fetchLineageData);
  }, [fetchLineageData]);

  const handleCopyHash = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Aggregated stat calculations
  const totalSources = report?.sources?.length || 0;
  const totalRawRows = report?.sources?.reduce((acc, s) => acc + s.raw_rows, 0) || 0;
  const totalAcceptedRows = report?.sources?.reduce((acc, s) => acc + s.accepted_rows, 0) || 0;
  const totalRejectedRows = report?.sources?.reduce((acc, s) => acc + s.rejected_rows, 0) || 0;

  const getLicenseBadgeStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case "mit":
        return "bg-emerald-950 text-emerald-400 border-emerald-800";
      case "owned":
        return "bg-cyan-950 text-cyan-400 border-cyan-800";
      case "check_required":
        return "bg-amber-950 text-amber-400 border-amber-800";
      case "demo_safe_subset":
        return "bg-slate-900 text-teal-300 border-teal-800";
      default:
        return "bg-slate-900 text-slate-400 border-slate-700";
    }
  };

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-black text-white flex items-center gap-2.5 tracking-tight">
                <GitBranch className="w-7 h-7 text-indigo-400" /> Data Lineage Center
              </h2>
              {isDemoFallback && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-950 text-amber-300 border border-amber-800 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> Seeded demo lineage
                </span>
              )}
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Track dataset sources, transformations, splits, and benchmark provenance for transparent AI security evaluation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchLineageData}
              disabled={loading}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition border border-slate-700 flex items-center gap-2"
            >
              <Database className="w-4 h-4 text-indigo-400" />
              {loading ? "Refreshing..." : "Refresh Lineage Metadata"}
            </button>
          </div>
        </div>

        {/* SECTION A: DATASET FINGERPRINT CARDS */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Hash className="w-4 h-4 text-indigo-400" /> Section A: Cryptographic Dataset Fingerprint
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Dataset Version</div>
              <div className="text-sm font-mono font-bold text-indigo-400 mt-1 truncate">
                {report?.dataset_version || "--"}
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl lg:col-span-2">
              <div className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
                <span>Dataset SHA256</span>
                {report?.dataset_sha256 && (
                  <button
                    onClick={() => handleCopyHash(report.dataset_sha256 || "")}
                    className="text-slate-500 hover:text-slate-300 transition flex items-center gap-1 text-[10px]"
                  >
                    <Copy className="w-3 h-3" /> {copied ? "Copied!" : "Copy"}
                  </button>
                )}
              </div>
              <div className="text-xs font-mono font-bold text-cyan-400 mt-1 truncate">
                {report?.dataset_sha256 || "N/A"}
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Total Sources</div>
              <div className="text-xl font-black text-white mt-0.5">{totalSources}</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Raw Imported Rows</div>
              <div className="text-xl font-black text-slate-300 mt-0.5">{totalRawRows.toLocaleString()}</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Accepted / Rejected</div>
              <div className="text-base font-black text-emerald-400 mt-0.5">
                {totalAcceptedRows.toLocaleString()}{" "}
                <span className="text-xs font-normal text-rose-400">/ {totalRejectedRows.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* SECTION B: SOURCE REGISTRY TABLE */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" /> Section B: Multi-Source Provenance Registry
            </h3>
            <span className="text-xs text-slate-500 font-mono">{totalSources} Verified Sources</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-3 border-b border-slate-800">Source ID</th>
                  <th className="p-3 border-b border-slate-800">Platform</th>
                  <th className="p-3 border-b border-slate-800">Purpose</th>
                  <th className="p-3 border-b border-slate-800">License Status</th>
                  <th className="p-3 border-b border-slate-800 text-right">Raw Rows</th>
                  <th className="p-3 border-b border-slate-800 text-right">Accepted</th>
                  <th className="p-3 border-b border-slate-800 text-right">Rejected</th>
                  <th className="p-3 border-b border-slate-800 min-w-[200px]">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 text-slate-300">
                {report?.sources?.map((src: DataSourceLineage) => (
                  <tr key={src.source_id} className="hover:bg-slate-950/60 transition">
                    <td className="p-3 font-mono font-bold text-cyan-400">{src.source_id}</td>
                    <td className="p-3 font-medium text-slate-300">{src.platform}</td>
                    <td className="p-3 text-slate-400">{src.purpose}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getLicenseBadgeStyle(
                          src.license_status
                        )}`}
                      >
                        {src.license_status}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-right text-slate-400">{src.raw_rows.toLocaleString()}</td>
                    <td className="p-3 font-mono text-right text-emerald-400 font-bold">
                      {src.accepted_rows.toLocaleString()}
                    </td>
                    <td className="p-3 font-mono text-right text-rose-400 font-bold">
                      {src.rejected_rows > 0 ? src.rejected_rows.toLocaleString() : "0"}
                    </td>
                    <td className="p-3 text-slate-400 text-[11px] leading-relaxed">{src.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* SECTION C: TRANSFORM PIPELINE FLOW */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-400" /> Section C: Data Engineering Transformation Pipeline
            </h3>
            <span className="text-xs text-slate-500 font-mono">8 Sequential Pipeline Stages</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {report?.stages?.map((stg: TransformStage, idx: number) => (
              <div
                key={stg.stage}
                className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2 relative group hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                  <span className="text-[10px] font-mono font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1">
                    <span className="w-4 h-4 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 flex items-center justify-center text-[9px]">
                      {idx + 1}
                    </span>
                    {stg.stage}
                  </span>
                  {stg.rejected_rows > 0 ? (
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-amber-950 text-amber-400 border border-amber-800">
                      -{stg.rejected_rows}
                    </span>
                  ) : (
                    <span className="text-[9px] font-mono text-emerald-400 font-bold">Pass</span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-1 text-[10px] pt-1 font-mono text-center">
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-850">
                    <div className="text-slate-500 text-[9px]">In</div>
                    <div className="font-bold text-slate-300">{stg.input_rows}</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-850">
                    <div className="text-slate-500 text-[9px]">Out</div>
                    <div className="font-bold text-emerald-400">{stg.output_rows}</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-850">
                    <div className="text-slate-500 text-[9px]">Rej</div>
                    <div className={`font-bold ${stg.rejected_rows > 0 ? "text-amber-400" : "text-slate-500"}`}>
                      {stg.rejected_rows}
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 leading-relaxed pt-1">{stg.reason}</div>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION D: DATASET DISTRIBUTIONS */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <PieChart className="w-4 h-4 text-cyan-400" /> Section D: Dataset Distribution Profiles
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Split Distribution */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-teal-400" /> Split Distribution
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(report?.split_distribution || {}).map(([split, val]) => (
                  <div
                    key={split}
                    className="bg-slate-950 border border-slate-850 p-3 rounded-lg flex items-center justify-between"
                  >
                    <span className="font-mono text-slate-300 capitalize">{split}</span>
                    <span className="font-bold font-mono text-teal-400">{val}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Label Distribution */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Label Distribution
              </h4>
              <div className="grid grid-cols-3 gap-2 text-xs">
                {Object.entries(report?.label_distribution || {}).map(([lbl, val]) => (
                  <div
                    key={lbl}
                    className="bg-slate-950 border border-slate-850 p-3 rounded-lg flex flex-col items-center justify-center"
                  >
                    <span className="font-mono text-slate-400 text-[10px] uppercase">{lbl}</span>
                    <span className="font-black font-mono text-emerald-400 text-base mt-0.5">{val}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Attack Type Distribution */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <FileCode className="w-3.5 h-3.5 text-rose-400" /> Attack Vector Breakdown
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                {Object.entries(report?.attack_type_distribution || {}).map(([atk, val]) => (
                  <div
                    key={atk}
                    className="bg-slate-950 border border-slate-850 p-2.5 rounded-lg flex items-center justify-between"
                  >
                    <span className="font-mono text-slate-400 text-[11px] truncate">{atk}</span>
                    <span className="font-bold font-mono text-rose-400 ml-1">{val}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Language Distribution */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-indigo-400" /> Target Language Coverage
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(report?.language_distribution || {}).map(([lang, val]) => (
                  <div
                    key={lang}
                    className="bg-slate-950 border border-slate-850 p-3 rounded-lg flex items-center justify-between"
                  >
                    <span className="font-mono text-slate-300 uppercase">Lang: {lang}</span>
                    <span className="font-bold font-mono text-indigo-400">{val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* SECTION E: NOTES / TRANSPARENCY */}
        {report?.notes && report.notes.length > 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-teal-400" /> Section E: Transparency & Audit Notes
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-400 font-mono">
              {report.notes.map((note: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 bg-slate-950 p-2.5 rounded border border-slate-850">
                  <span className="text-teal-400 font-bold">•</span>
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </AppShell>
  );
}
